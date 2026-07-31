from pydantic import BaseModel,Field,field_validator,model_validator,computed_field
from typing import List


class ResumeData(BaseModel):

    Skills : List[str] = Field(...,description ='List of skills')

    Age : int = Field(...,gt=20,le=60)

    Projects : List[str] = Field(...,description = "List of projects")

    GivenName : str = Field(...,description="The name they provided")

    RegisteredName : str = Field(...,description='The name company registered')

    @computed_field
    @property
    def salary(self)->int:
        return len(self.Skills)*len(self.Projects)*1000


    @model_validator(mode='after')
    def check_name(cls,data):
        if data.GivenName!=data.RegisteredName:
            raise ValueError("Name Mismatch")
        return data
    @field_validator('Skills')    
    def field_check(cls,data):
        
        if(len(data)<3):
            raise ValueError("Skills not upto the level")
        return data
    

class Candidate(ResumeData):

    UserID : int =Field(..., description='The unique candidate id')

    Domain : str = Field(...,description='The name of the domain' )




CandidateDetails=Candidate(UserID=124567,Domain="Data Science",Skills=["SQL","Pyspark","Pandas"],Age=21,Projects=["Nutriction Tracker","ETL pipeline"]
                           ,GivenName="Jackson Divakar",RegisteredName="Jackson Divakar")

print(CandidateDetails)


