import dspy
import config

from signature import CreditAssistant
from tools import (
    get_kyc_status,
    create_credit_request,
    check_status,
    set_delivery_method,
    verify_track
)

# ReAct Agent
react_agent = dspy.ReAct(
    signature=CreditAssistant,
    tools=[
        get_kyc_status,
        create_credit_request,
        check_status,
        set_delivery_method,
        verify_track
    ],
    max_iters=5
)