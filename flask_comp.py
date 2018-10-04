# -*- coding: utf-8 -*-
import perf_compare
import pygal
from flask import Flask, jsonify, render_template, request, abort
from pygal.style import Style

app = Flask(__name__)

custom_style = Style(
  #background='transparent',
  #plot_background='transparent',
  foreground='#53E89B',
  foreground_strong='#53A0E8',
  foreground_subtle='#630C0D',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  colors=('#E853A0', '#00FF80')
  )

NOGRAPH = """
<h3>No graph for %s. One or both datasets couldn't be fetched</h3>
"""

GRAPH = """
<body class="body">
    <div class="container" align="left">
<embed type="image/svg+xml" src=%s style='max-width:1000px'/>
    </div>
</body>
"""


def get_table(d):
    return render_template('table.html', data=d)


def graph(x, name):
    bar_chart = pygal.Bar(style=custom_style)
    bar_chart.title = 'Chart of deltas for %s' % name.capitalize()
    bar_chart.x_labels = [i[0] for i in x]
    bar_chart.add('Bad', [i[1] for i in x])
    bar_chart.add('Good', [i[2] for i in x])
    result = bar_chart.render_data_uri()
    return GRAPH % result


@app.route('/compare', methods=['GET'])
def compare():
    good = request.args.get('good')
    bad = request.args.get('bad')
    if not good or not bad:
        abort(404)
    data = perf_compare.compare(good, bad)
    result = ''
    for i in data:
        if not data[i]:
            result += NOGRAPH % i
        else:
            result += graph(data[i], i)
    table = get_table(data)
    return result + "<br><br><br>" + table


@app.route("/")
def index():
    return render_template('compare.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")
