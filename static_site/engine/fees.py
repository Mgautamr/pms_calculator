"""PMS fee engine.

Follows the conventions in the reference workbook exactly:
- Annual periods, fees charged at year end, no contributions or withdrawals.
- Fixed fee is a % of the opening value, charged even in loss years.
- Performance fee is measured on profit after the fixed fee, against a base
  (the opening value, or the high-water mark if hwm is True).
- A hurdle is a % of the base. Without catch-up, only profit above the hurdle
  is charged. With catch-up, once profit beats the hurdle the whole profit
  is charged.
- The exit load is charged once, on the final closing value.
"""


def simulate(initial, gross_returns, fixed_fee, perf_fee, hurdle,
             catch_up, hwm, exit_load):
    """Run a fee scenario year by year.

    All percentages are decimals (0.025 means 2.5%).
    Returns a dict with the year-end values and the totals.
    """
    value = initial              # opening value of the current year
    high_water_mark = initial    # highest closing value so far
    closing_values = []
    fixed_fees = []
    perf_fees = []
    total_fixed = 0.0
    total_perf = 0.0

    for r in gross_returns:
        value_before_fees = value * (1 + r)
        fixed = value * fixed_fee

        base = high_water_mark if hwm else value
        profit = value_before_fees - fixed - base
        hurdle_amount = base * hurdle

        if catch_up:
            perf = perf_fee * profit if profit > hurdle_amount else 0.0
        else:
            perf = perf_fee * max(0.0, profit - hurdle_amount)

        value = value_before_fees - fixed - perf
        high_water_mark = max(high_water_mark, value)

        closing_values.append(value)
        fixed_fees.append(fixed)
        perf_fees.append(perf)
        total_fixed += fixed
        total_perf += perf

    exit_amount = value * exit_load
    final_net_value = value - exit_amount
    total_fees = total_fixed + total_perf + exit_amount

    return {
        "closing_values": closing_values,
        "fixed_fees": fixed_fees,
        "perf_fees": perf_fees,
        "exit_amount": exit_amount,
        "final_net_value": final_net_value,
        "total_fees": total_fees,
    }
