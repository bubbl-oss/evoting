"""Functions or tools we may use more than once

"""
from datetime import datetime


# I don't know if this is illegal in Python ^.^
# passing whole ass objects like this :shrug:
def calculate_election_result(election, Result, db):
    """Calculate Election Result

        Returns: 
        - a new Result object that you should save or if the Result
        already exists, it updates it and returns None. So you can carry on with your exection
    """
# user wants to change their election to ending. As per, the election is over
# so now, calculate the results
#
# to calculate results of an election, count all the votes per candidate and then create the Result object
# with that number
# --- Do it for each of the Positions ---
    for p in election.positions:

        # Was checking if the candidates were greater than 1 before lol... I felt
        # you should'nt be able to calculate results when candidates is only 1
        if p.candidates.count() > 0:
            for c in p.candidates:
                total_votes = c.votes.count()
                # find the result if it exists and update it!
                current_result = Result.query.filter_by(position_id=p.id,
                                                        candidate_id=c.id).first()
                if current_result is not None:
                    # just update it if it already exists
                    current_result.total_votes = total_votes
                    current_result.modified_at = datetime.now()
                else:
                    # if the result doesn't exist yet, create a new one.
                    r = Result(position_id=p.id,
                               candidate_id=c.id, total_votes=total_votes)
                    db.session.add(r)
            try:
                db.session.commit()
            except:
                db.session.rollback()

# delete all data in tables...
# TODO: add citation!


def clear_data(db):
    """Clear all the data in the tables without dropping the tables
    """
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s', table)
        db.session.execute(table.delete())
    db.session.commit()
