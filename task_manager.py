#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("tasks.json")


class TaskManager:
    def __init__(self, file_path=DATA_FILE):
        self.file_path = Path(file_path)
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        self.file_path.write_text("[]", encoding="utf-8")
        return []

    def save_tasks(self):
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=2)
            file.write("\n")

    def add_task(self, title):
        task = {
            "id": self._next_id(),
            "title": title.strip(),
            "completed": False,
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def list_tasks(self):
        return self.tasks

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                return task
        return None

    def delete_task(self, task_id):
        original_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        if len(self.tasks) != original_count:
            self.save_tasks()
            return True
        return False

    def _next_id(self):
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1


def build_parser():
    parser = argparse.ArgumentParser(description="Simple task manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("title", help="Task title")

    subparsers.add_parser("list", help="List all tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("id", type=int, help="Task id")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task id")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    manager = TaskManager()

    if args.command == "add":
        task = manager.add_task(args.title)
        print(f"Added task #{task['id']}: {task['title']}")
        return 0

    if args.command == "list":
        tasks = manager.list_tasks()
        if not tasks:
            print("No tasks yet.")
            return 0

        for task in tasks:
            status = "✓" if task["completed"] else " "
            print(f"#{task['id']} [{status}] {task['title']}")
        return 0

    if args.command == "complete":
        task = manager.complete_task(args.id)
        if task is None:
            print(f"Task #{args.id} was not found.")
            return 1
        print(f"Completed task #{task['id']}: {task['title']}")
        return 0

    if args.command == "delete":
        deleted = manager.delete_task(args.id)
        if not deleted:
            print(f"Task #{args.id} was not found.")
            return 1
        print(f"Deleted task #{args.id}.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
