from pydantic import BaseModel, validator

class BloodDonationRow(BaseModel):
    recency_months: int
    frequency_times: int
    monetary_cc_blood: int
    time_months: int

    @validator('recency_months')
    def recency_check(cls, v):
        if v >= 0 and v <= 74:
            return v
        raise ValueError('Recency must be between 0 and 74')

    @validator('frequency_times')
    def frequency_check(cls, v):
        if v >= 1 and v <= 50:
            return v
        raise ValueError('Frequency must be between 1 and 50')

    @validator('monetary_cc_blood')
    def monetary_check(cls, v):
        if v >= 250 and v <= 12500:
            return v
        raise ValueError('Monetary must be between 250 and 12500')

    @validator('time_months')
    def time_check(cls, v):
        if v >= 2 and v <= 98:
            return v
        raise ValueError('Time must be between 2 and 98')