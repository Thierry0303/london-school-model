# Probability and Demand Modeling Functions

def probability_of_event(event_count, total_count):
    """
    Calculate the probability of an event occurring.
    :param event_count: Number of successful events
    :param total_count: Total number of events
    :return: Probability of the event
    """
    if total_count == 0:
        return 0
    return event_count / total_count


def demand_modeling(demand_params, time_period):
    """
    Model potential demand over a given time period.
    :param demand_params: Dictionary containing demand parameters (e.g., base_demand, growth_rate)
    :param time_period: Time period for which to model demand
    :return: Estimated demand over time period
    """
    base_demand = demand_params.get('base_demand', 0)
    growth_rate = demand_params.get('growth_rate', 0)
    estimated_demand = base_demand * (1 + growth_rate) ** time_period
    return estimated_demand
