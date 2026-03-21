# School Scoring Algorithms

# This module contains various algorithms to calculate scores for schools based on different criteria.


def calculate_average_score(students_scores):
    """ Calculate the average score of students. """
    if not students_scores:
        return 0
    return sum(students_scores) / len(students_scores)


def calculate_weighted_score(students_scores, weights):
    """ Calculate weighted scores for students based on given weights. """
    if not students_scores or len(students_scores) != len(weights):
        return 0
    return sum(score * weight for score, weight in zip(students_scores, weights))


def determine_pass_fail(score, passing_score=50):
    """ Determine if the score is a pass or fail. """
    return "Pass" if score >= passing_score else "Fail"