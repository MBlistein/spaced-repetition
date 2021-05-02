"""
DEPRECATED after v0.1 --> to be revived in the future

This script serves a simulator for different learning paths.
Given a series of problem solving results, it plots the ease and spacing
interval development.
The produced plots can be used to understand and calibrate the spaced
repetition algorithm's parameters.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.gridspec import GridSpec
from tabulate import tabulate

from spaced_repetition.domain.problem_log import (
    ProblemLogCreator,
    Result)
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.get_problem_log import SuperMemo2

DEFAULT_INTERVAL = {
    Result.KNEW_BY_HEART: SuperMemo2.INTERVAL_KNEW_BY_HEART,
    Result.SOLVED_OPTIMALLY_IN_UNDER_25: SuperMemo2.INTERVAL_SOLVED_OPTIMALLY_IN_UNDER_25,
    Result.SOLVED_OPTIMALLY_SLOWER: SuperMemo2.INTERVAL_SOLVED_OPTIMALLY_SLOWER,
    Result.SOLVED_OPTIMALLY_WITH_HINT: SuperMemo2.INTERVAL_NON_OPTIMAL_SOLUTION,
    Result.SOLVED_SUBOPTIMALLY: SuperMemo2.INTERVAL_NON_OPTIMAL_SOLUTION,
    Result.NO_IDEA: SuperMemo2.INTERVAL_NON_OPTIMAL_SOLUTION
}


new_topic_path = [
    Result.NO_IDEA,
    Result.SOLVED_OPTIMALLY_SLOWER,
    Result.KNEW_BY_HEART,
    Result.SOLVED_OPTIMALLY_WITH_HINT,
    Result.SOLVED_OPTIMALLY_IN_UNDER_25,
    Result.KNEW_BY_HEART]
known_topic_path = [
    Result.SOLVED_OPTIMALLY_SLOWER,
    Result.SOLVED_OPTIMALLY_IN_UNDER_25,
    Result.KNEW_BY_HEART,
    Result.SOLVED_OPTIMALLY_IN_UNDER_25,
    Result.KNEW_BY_HEART,
]


def run():
    data = spacing_data(new_topic_path)
    plot_spacing(data)


def spacing_data(repetition_results) -> pd.DataFrame:
    data = []
    last_log = None
    current_day = 0
    repetition_cnt = 0

    for result in repetition_results:
        print(f'\n----------------{result}-----------------')
        last_log = ProblemLogCreator.create(
            problem_id=1,
            result=result,
            tags=[TagCreator.create('dummy_tag')])
        data.append({'day': current_day,
                     'repetition': repetition_cnt,
                     'result': last_log.result})

        repetition_cnt += 1

    print(tabulate(data, headers='keys'))
    return pd.DataFrame(data=data)


def plot_spacing(df):
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle('Spacing development')
    g_s = GridSpec(nrows=2, ncols=2, figure=fig,
                  hspace=0.3, wspace=0.25)

    ax0 = fig.add_subplot(g_s[0, 0])
    ax1 = plt.subplot(g_s.new_subplotspec((0, 1), colspan=1))
    ax2 = plt.subplot(g_s.new_subplotspec((1, 0), colspan=2))

    sns.scatterplot(ax=ax0, data=df, x='repetition', y='ease',
                    hue='result', marker='o', zorder=2)
    sns.lineplot(ax=ax0, data=df, x='repetition', y='ease',
                 zorder=1)
    style_background_line(ax0)
    ax0.set_title('ease')
    ax0.get_legend().remove()
    ax0.set_ylim([0, df.ease.max() * 1.1])

    sns.scatterplot(ax=ax1, data=df, x='repetition', y='interval',
                    hue='result', marker='o', zorder=2)
    sns.lineplot(ax=ax1, data=df, x='repetition', y='interval',
                 zorder=1)
    style_background_line(ax1)
    ax1.set_title('interval')
    ax1.set_ylim([0, df.interval.max() * 1.05])
    ax1.get_legend().remove()

    sns.scatterplot(ax=ax2, data=df, x='day', y='interval',
                    hue='result', marker='o', zorder=2)
    sns.lineplot(ax=ax2, data=df, x='day', y='interval',
                 zorder=1)
    style_background_line(ax2)
    ax2.set_ylim([0, df.interval.max() * 1.05])
    ax2.set_title('repetition timeline')

    plt.show()


def style_background_line(ax):
    ax.lines[0].set_linestyle('dotted')
    ax.lines[0].set_color('grey')


if __name__ == "__main__":
    run()
