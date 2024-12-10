from Utilities.Enums.BaseEnum import BaseEnum


class RequestStatus(BaseEnum):
    APPLIED = "Applied"
    IN_PROCESS = "In Process"
    APPROVED = "Approved"
    DECLINED = "Declined"
    COMPLETED = "Completed"
