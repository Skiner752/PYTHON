# Implementation for cool progress bar
import sys

class ProgressBar:
    def displayProgressBar(iteration, total, bar_length=50):
        progress = (iteration / total)
        arrow = '=' * int(round(progress * bar_length) - 1)
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write(f'\rProgress: [{arrow + spaces}] {iteration}/{total}')
        sys.stdout.flush()