from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Optional

# from base import LilacReader
from pydantic import BaseModel

"""Lilac reader that loads enriched and labeled Lilac datasets into GPTIndex and LangChain."""
from typing import List, Optional
from typing import TYPE_CHECKING, Optional

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

if TYPE_CHECKING:
    from lilac import FilterLike, Path, ColumnId


class LilacReader(BaseReader):
    """
    Lilac dataset reader
    """

    def load_data(
        self,
        dataset: str,
        text_path: "Path" = "text",
        doc_id_path: Optional["Path"] = "doc_id",
        columns: Optional[List["ColumnId"]] = None,
        filters: Optional[List["FilterLike"]] = None,
        project_dir: Optional[str] = None,
    ) -> List[Document]:
        """
        Load text from relevant posts and top-level comments in subreddit(s), given keyword(s) for search

        Args:
            project_dir (Optional[str]): The Lilac project dir to read from. If not defined, uses the `LILAC_PROJECT_DIR`
              environment variable.
            text_path: The path to the text field in the dataset. If not defined, uses 'text'.
            columns (Optional[List[ColumnId]]): The columns to load from the dataset. If not defined, loads all columns.
            dataset (str): The dataset to load. Should be formatted like {namespace}/{dataset_name}.
            filters (Optional[Filter]): A filter to apply to the dataset before loading into documents. Useful to filter
              for labeled data.

        """

        try:
            import lilac as ll
        except ImportError:
            raise ("`lilac` package not found, please run `pip install lilac`")

        namespace, dataset_name = dataset.split("/")
        lilac_dataset = ll.get_dataset(namespace, dataset_name, project_dir=project_dir)

        # Check to make sure text path, and doc_id path are valid.
        manifest = lilac_dataset.manifest()

        text_path = ll.normalize_path(text_path)
        text_field = manifest.data_schema.get_field(text_path)
        if not text_field:
            raise ValueError(
                f"Could not find text field {text_path} in dataset {dataset}"
            )

        doc_id_path = ll.normalize_path(doc_id_path)
        doc_id_field = manifest.data_schema.get_field(doc_id_path)
        if not doc_id_field:
            raise ValueError(
                f"Could not find doc_id field {doc_id_path} in dataset {dataset}"
            )

        rows = lilac_dataset.select_rows(
            columns=(columns + [text_field, doc_id_path]) if columns else ["*"],
            filters=filters,
            combine_columns=True,
        )

        def _item_from_path(item: ll.Item, path: ll.PathTuple) -> ll.Item:
            if len(path) == 1:
                item = item[path[0]]
                if isinstance(item, dict):
                    return item[ll.VALUE_KEY]
                else:
                    return item
            else:
                return _item_from_path(item[path[0]], path[1:])

        def _remove_item_path(item: ll.Item, path: ll.PathTuple) -> None:
            if len(path) == 0:
                return
            if len(path) == 1:
                if item and path[0] in item:
                    leaf_item = item[path[0]]
                    if isinstance(leaf_item, dict):
                        del item[path[0]][ll.VALUE_KEY]
                    else:
                        del item[path[0]]
                return
            else:
                _remove_item_path(item[path[0]], path[1:])

        documents: List[Document] = []
        for row in rows:
            text = _item_from_path(row, text_path)
            doc_id = _item_from_path(row, doc_id_path)
            _remove_item_path(row, text_path)
            _remove_item_path(row, doc_id_path)
            documents.append(Document(text=text, doc_id=doc_id, extra_info=row or {}))

        return documents


app = FastAPI(openapi_url="/api/v1/openapi.json")


class DocumentModel(BaseModel):
    text: str
    doc_id: Optional[str] = None
    extra_info: Optional[dict] = {}


def get_lilac_reader_dependency():
    try:
        return LilacReader()
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/load_data", response_model=List[DocumentModel])
def load_data(
    dataset: str = Query(
        ..., description="The dataset to load, formatted as {namespace}/{dataset_name}"
    ),
    text_path: str = Query("text", description="Path to the text field in the dataset"),
    doc_id_path: Optional[str] = Query(
        None, description="Path to the document ID field in the dataset"
    ),
    columns: Optional[List[str]] = Query(
        None, description="Columns to load from the dataset"
    ),
    filters: Optional[List[str]] = Query(
        None, description="Filters to apply to the dataset before loading"
    ),
    project_dir: Optional[str] = Query(
        None, description="Lilac project directory to read from"
    ),
    lilac_reader: LilacReader = Depends(get_lilac_reader_dependency),
):
    try:
        documents = lilac_reader.load_data(
            dataset=dataset,
            text_path=text_path,
            doc_id_path=doc_id_path,
            columns=columns,
            filters=filters,
            project_dir=project_dir,
        )
        return [DocumentModel(**doc.dict()) for doc in documents]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
