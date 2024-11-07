from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import requests
import json


class CreateNoteRequest(BaseModel):
    title: str
    content: str


class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    modified_at: datetime


class NoteWithoutContent(BaseModel):
    id: int
    title: str
    created_at: datetime
    modified_at: datetime


class AttachNoteRequest(BaseModel):
    child_note_id: int
    parent_note_id: int
    hierarchy_type: str


class NoteHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class Tag(BaseModel):
    id: int
    name: str


class CreateTagRequest(BaseModel):
    name: str


class AttachTagRequest(BaseModel):
    note_id: int
    tag_id: int


class NoteTagRelation(BaseModel):
    note_id: int
    tag_id: int


class TagHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class AttachTagHierarchyRequest(BaseModel):
    parent_id: int
    child_id: int


class TreeTag(BaseModel):
    id: int
    name: str


class TreeNote(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    hierarchy_type: Optional[str] = None
    children: list["TreeNote"] = []
    tags: list[TreeTag] = []


class TreeTagWithNotes(BaseModel):
    id: int
    name: str
    children: list["TreeTagWithNotes"] = []
    notes: list["TreeNote"] = []


def update_notes_tree(
    notes: list[TreeNote], base_url: str = "http://localhost:37240"
) -> None:
    """
    Update the entire notes tree structure

    Args:
        notes: List of TreeNote objects representing the new tree structure
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.put(
        f"{base_url}/notes/tree",
        headers={"Content-Type": "application/json"},
        json=[note.model_dump(exclude_unset=True) for note in notes],
    )

    response.raise_for_status()


def note_create(
    title: str, content: str, base_url: str = "http://localhost:37240"
) -> dict:
    """
    Create a new note using the API

    Args:
        title: The title of the note
        content: The content of the note
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        dict: The created note data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateNoteRequest(title=title, content=content)

    response = requests.post(
        f"{base_url}/notes/flat",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return response.json()


def get_note(note_id: int, base_url: str = "http://localhost:37240") -> Note:
    """
    Retrieve a note by its ID

    Args:
        note_id: The ID of the note to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Note: The retrieved note data

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Note.model_validate(response.json())


def get_note_without_content(
    note_id: int, base_url: str = "http://localhost:37240"
) -> NoteWithoutContent:
    """
    Retrieve a note by its ID, excluding the content field

    Args:
        note_id: The ID of the note to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        NoteWithoutContent: The retrieved note data without content

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}",
        params={"exclude_content": "true"},
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return NoteWithoutContent.model_validate(response.json())


def get_all_notes(base_url: str = "http://localhost:37240") -> list[Note]:
    """
    Retrieve all notes

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Note]: List of all notes

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Note.model_validate(note) for note in response.json()]


def get_all_notes_without_content(
    base_url: str = "http://localhost:37240",
) -> list[NoteWithoutContent]:
    """
    Retrieve all notes without their content

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteWithoutContent]: List of all notes without content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat",
        params={"exclude_content": "true"},
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteWithoutContent.model_validate(note) for note in response.json()]


def attach_note_to_parent(
    child_note_id: int,
    parent_note_id: int,
    hierarchy_type: str = "block",
    base_url: str = "http://localhost:37240",
) -> None:
    """
    Attach a note as a child of another note

    Args:
        child_note_id: ID of the note to attach as child
        parent_note_id: ID of the parent note
        hierarchy_type: Type of hierarchy relationship (default: "block")
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachNoteRequest(
        child_note_id=child_note_id,
        parent_note_id=parent_note_id,
        hierarchy_type=hierarchy_type,
    )

    response = requests.post(
        f"{base_url}/notes/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def get_note_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[NoteHierarchyRelation]:
    """
    Get all parent-child relationships between notes

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteHierarchyRelation]: List of all parent-child relationships

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteHierarchyRelation.model_validate(rel) for rel in response.json()]


def detach_note_from_parent(
    note_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a note from its parent

    Args:
        note_id: ID of the note to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/notes/hierarchy/detach/{note_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_tag(tag_id: int, base_url: str = "http://localhost:37240") -> Tag:
    """
    Get a tag by its ID

    Args:
        tag_id: The ID of the tag to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The retrieved tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def get_all_tags(base_url: str = "http://localhost:37240") -> list[Tag]:
    """
    Get all tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Tag]: List of all tags

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Tag.model_validate(tag) for tag in response.json()]


def update_tag(tag_id: int, name: str, base_url: str = "http://localhost:37240") -> Tag:
    """
    Update an existing tag

    Args:
        tag_id: The ID of the tag to update
        name: The new name for the tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The updated tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateTagRequest(name=name)

    response = requests.put(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def delete_tag(tag_id: int, base_url: str = "http://localhost:37240") -> None:
    """
    Delete a tag by its ID

    Args:
        tag_id: The ID of the tag to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def attach_tag_to_note(
    note_id: int, tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a tag to a note

    Args:
        note_id: The ID of the note
        tag_id: The ID of the tag to attach
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTagRequest(note_id=note_id, tag_id=tag_id)

    response = requests.post(
        f"{base_url}/tags/notes",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_tag_from_note(
    note_id: int, tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a tag from a note

    Args:
        note_id: The ID of the note
        tag_id: The ID of the tag to detach
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/notes/{note_id}/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_note_tag_relations(
    base_url: str = "http://localhost:37240",
) -> list[NoteTagRelation]:
    """
    Get all relationships between notes and tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteTagRelation]: List of all note-tag relationships

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/notes",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteTagRelation.model_validate(rel) for rel in response.json()]


def get_tag_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[TagHierarchyRelation]:
    """
    Get all parent-child relationships between tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TagHierarchyRelation]: List of all parent-child relationships between tags

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TagHierarchyRelation.model_validate(rel) for rel in response.json()]


def attach_tag_to_parent(
    child_id: int, parent_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a tag as a child of another tag

    Args:
        child_id: ID of the tag to attach as child
        parent_id: ID of the parent tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTagHierarchyRequest(child_id=child_id, parent_id=parent_id)

    response = requests.post(
        f"{base_url}/tags/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_tag_from_parent(
    tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a tag from its parent

    Args:
        tag_id: ID of the tag to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/hierarchy/detach/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def create_tag(name: str, base_url: str = "http://localhost:37240") -> Tag:
    """
    Create a new tag

    Args:
        name: The name of the tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The created tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateTagRequest(name=name)

    response = requests.post(
        f"{base_url}/tags",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def get_tags_tree(base_url: str = "http://localhost:37240") -> list[TreeTagWithNotes]:
    """
    Get all tags in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeTagWithNotes]: List of all tags with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeTagWithNotes.model_validate(tag) for tag in response.json()]


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class CreateTaskRequest(BaseModel):
    note_id: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO
    effort_estimate: Optional[Decimal] = None
    actual_effort: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    all_day: bool = False
    goal_relationship: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    note_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    effort_estimate: Optional[Decimal] = None
    actual_effort: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    all_day: Optional[bool] = None
    goal_relationship: Optional[str] = None


class AttachTaskRequest(BaseModel):
    child_task_id: int
    parent_task_id: int


class TaskHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class TreeTask(BaseModel):
    id: int
    note_id: Optional[int]
    status: TaskStatus
    effort_estimate: Optional[Decimal]
    actual_effort: Optional[Decimal]
    deadline: Optional[datetime]
    priority: Optional[int]
    created_at: datetime
    modified_at: datetime
    all_day: bool
    goal_relationship: Optional[str]
    children: list["TreeTask"] = []


class Task(BaseModel):
    id: int
    note_id: Optional[int]
    status: TaskStatus
    effort_estimate: Optional[Decimal]
    actual_effort: Optional[Decimal]
    deadline: Optional[datetime]
    priority: Optional[int]
    created_at: datetime
    modified_at: datetime
    all_day: bool
    goal_relationship: Optional[str]


def get_task(task_id: int, base_url: str = "http://localhost:37240") -> Task:
    """
    Get a task by its ID

    Args:
        task_id: The ID of the task to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The retrieved task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def get_all_tasks(base_url: str = "http://localhost:37240") -> list[Task]:
    """
    Get all tasks

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Task]: List of all tasks

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Task.model_validate(task) for task in response.json()]


def get_task_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[TaskHierarchyRelation]:
    """
    Get all parent-child relationships between tasks

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TaskHierarchyRelation]: List of all parent-child relationships between tasks

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TaskHierarchyRelation.model_validate(rel) for rel in response.json()]


def update_task(
    task_id: int, task: UpdateTaskRequest, base_url: str = "http://localhost:37240"
) -> Task:
    """
    Update an existing task

    Args:
        task_id: The ID of the task to update
        task: The task data to update
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The updated task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.put(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
        data=task.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def delete_task(task_id: int, base_url: str = "http://localhost:37240") -> None:
    """
    Delete a task by its ID

    Args:
        task_id: The ID of the task to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the task is not found (404)
    """
    response = requests.delete(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def create_task(
    task: CreateTaskRequest, base_url: str = "http://localhost:37240"
) -> Task:
    """
    Create a new task

    Args:
        task: The task data to create
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The created task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.post(
        f"{base_url}/tasks",
        headers={"Content-Type": "application/json"},
        data=task.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def attach_task_to_parent(
    child_id: int, parent_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a task as a child of another task

    Args:
        child_id: ID of the task to attach as child
        parent_id: ID of the parent task
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTaskRequest(child_task_id=child_id, parent_task_id=parent_id)

    response = requests.post(
        f"{base_url}/tasks/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_task_from_parent(
    task_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a task from its parent

    Args:
        task_id: ID of the task to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tasks/hierarchy/detach/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_tasks_tree(base_url: str = "http://localhost:37240") -> list[TreeTask]:
    """
    Get all tasks in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeTask]: List of all tasks with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeTask.model_validate(task) for task in response.json()]


def get_notes_tree(base_url: str = "http://localhost:37240") -> list[TreeNote]:
    """
    Retrieve all notes in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeNote]: List of all notes with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeNote.model_validate(note) for note in response.json()]