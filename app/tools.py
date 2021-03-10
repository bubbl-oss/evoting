"""Functions or tools we may use more than once

"""
from datetime import datetime
from app.models import Result


def calculate_election_result(election):
    """Calculate Election Result

        Returns: 
        - a new Result object that you should save or if the Result
        already exists, it updates it and returns None. So you can carry on with your exection
    """
# user wants to change their election to ending. As per, the election is over
# so now, calculate the results
#
# to calculate results of an election, count all the votes per candidate and then add them
    if election.candidates.count() > 1:
        for c in election.candidates:
            total_votes = c.votes.count()
            # find the result if it exists and update it!
            current_result = Result.query.filter_by(election_id=election.id,
                                                    candidate_id=c.id).first()
            if current_result is not None:
                # just update it if it already exists
                current_result.total_votes = total_votes
                current_result.modified_at = datetime.now()
            else:
                return Result(election_id=election.id,
                              candidate_id=c.id, total_votes=total_votes)
