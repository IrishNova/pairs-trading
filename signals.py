import pandas as pd


def generate_signals(z, entry=2.0, exit=0.0, stop=3.0):
    positions = []
    trades = []
    position = 0
    entry_date = None
    armed = True                                   # may we open a new position?

    for dt, zt in z.items():
        if position == 0:                          # flat
            if not armed and abs(zt) < entry:
                armed = True                       # spread back in the band -> re-arm

            if armed:                              # look for entry
                if zt > entry:
                    position, entry_date = -1, dt  # spread too high -> SHORT it
                elif zt < -entry:
                    position, entry_date = 1, dt   # spread too low  -> LONG it

        elif position == 1:                        # long spread
            if zt >= exit or zt < -stop:           # reverted to mean, or stopped out
                trades.append((entry_date, dt, position))
                position, armed = 0, False         # disarm until z returns to the band

        elif position == -1:                       # short spread
            if zt <= exit or zt > stop:            # reverted to mean, or stopped out
                trades.append((entry_date, dt, position))
                position, armed = 0, False         # disarm until z returns to the band

        positions.append(position)

    return (pd.Series(positions, index=z.index),
            pd.DataFrame(trades, columns=['entry_date', 'exit_date', 'direction']))
