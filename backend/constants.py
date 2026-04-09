from enum import Enum

class WorkOrderStatus(str, Enum):
    BACKLOG = "Backlog"
    IN_PROGRESS = "InProgress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

class HealthStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class UserRole(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    WORKER = "Worker"

class Department(str, Enum):
    TECH = "技术部"
    PROCESS = "工艺部"
    PURCHASING = "采购部"
    PRODUCTION = "生产部"
    PROJECT = "项目管理部"

class ChangeType(str, Enum):
    TECHNICAL = "技术变更"
    PROCESS = "工艺变更"
    SCHEDULE = "计划变更"
