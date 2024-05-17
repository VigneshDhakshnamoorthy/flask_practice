from flask import Flask, Response, jsonify, render_template, request
from database_helper import DatabaseHelper

app = Flask(__name__)

db_name = './database/wsr.db'

db_helper = DatabaseHelper(db_name)


@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/edit')
def edit() -> str:
    return render_template('edit.html')

@app.route('/save_data', methods=['POST'])
def save_data() -> str:
    if request.method == 'POST':
        project = request.json['project']
        week = request.json['week']
        print(request.json)
        def save_to_table(table_name, data):
            project = request.json['project']
            week = request.json['week']
            data_to_save = [(project, week) + tuple(row) for row in data]
            db_helper.save_data(table_name, db_helper.get_table_dict()[table_name],data_to_save)

        save_to_table('utilization_by_task', request.json['utilization_by_task'])
        save_to_table('utilization_by_resource', request.json['utilization_by_resource'])
        save_to_table('task_last_week', request.json['task_last_week'])
        save_to_table('task_current_week', request.json['task_current_week'])
        save_to_table('week_defect_summary', request.json['week_defect_summary'])
        save_to_table('activity_this_week', request.json['activity_this_week'])

        return 'Data saved successfully'

@app.route('/fetch_data', methods=['POST'])
def fetch_data() -> Response:
    project = request.json['project']
    week = request.json['week']
    data = {}
    for table_name in db_helper.get_table_names():
        data[table_name] = db_helper.fetch_data(table_name, 'project=? AND week=?', (project, week))
    return jsonify(data)

@app.route('/update_data', methods=['POST'])
def update_data() -> str:
    project = request.json['project']
    week = request.json['week']

    def update_table(table_name, data):
        for row in data:
            id = row.pop('id')  # Remove ID from the row
            db_helper.update_data(table_name, ', '.join([f"{key}=? " for key in row.keys()]), 'id=?', tuple(row.values()) + (id,))

    update_table('utilization_by_task', request.json['utilization_by_task'])
    update_table('utilization_by_resource', request.json['utilization_by_resource'])
    update_table('task_last_week', request.json['task_last_week'])
    update_table('task_current_week', request.json['task_current_week'])
    update_table('week_defect_summary', request.json['week_defect_summary'])
    update_table('activity_this_week', request.json['activity_this_week'])

    return 'Data updated successfully'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6968, threaded=True)
