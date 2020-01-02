import machine
import json
import utime
import tinyweb
import _thread


class Config():
    """
    Config file operations endpoint
    """
    def get(self, data):
        """
        Show configs
        """
        return CONFIG, 200

    def post(self, data):
        """
        Save config to file
        """
        print(data)
        if save_config_to_disk(data):
            return {'message': 'saved'}, 201
        else:
            return {'message': 'not_saved'}, 500

    def delete(self, data):
        """
        Delete config from filer
        """
        if delete_config_from_disk():
            return {'message': 'deleted'}, 200
        else:
            return {'message': 'not_deleted'}, 500


class Reset():
    """
    System reset endpoint
    """
    def put(self, data):
        """Reset system"""
        machine.reset()

    def post(self, data):
        """Reset system"""
        machine.reset()

    def get(self, data):
        """Reset system"""
        machine.reset()


class FileSystem():
    """
    Simple file system operations endpoint
    Need to verify files content
    """
    def get(self, data, file_name):
        """Get File Content"""
        print(file_name)
        try:
            with open(file_name) as file_handler:
                config_content = file_handler.read()
                return {file_name: config_content}
        except Exception as Ex:
            return {"error": Ex}, 500


# Create web server instance
app = tinyweb.webserver()


@app.route('/')
async def index(request, response):
    await response.start_html()
    # Just simple form, will be replaced with JavaScript-based page
    await response.send('<!DOCTYPE html>\n'
                        '<html>\n'
                        '<body>\n'
                        '<LINK href="/static/main.css" rel="stylesheet" type="text/css">\n'
                        '<h1>DCC ACCESSORIES: Turnout controller</h1>\n'
                        '<h3>https://github.com/sirmax123/dccpi-mm</h3>\n'
                        '<H2>Configure Devices</H2>\n'
                        '<BR>\n'
                        '<form action="api/v1/config" method="POST">\n')
    for k, v in CONFIG.items():
        if isinstance(v, dict):
            await response.send('{key} \n <input type="text" name="{key}" value="{value}"><br>\n'.format(key=k,
                                                                                                         value=json.dumps(v)))
        elif isinstance(v, str):
            await response.send('{key} \n <input type="text" name="{key}" value="{value}"><br>\n'.format(key=k,
                                                                                                         value=v))
        else:
            pass
    await response.send('<br><br><input type="submit" value="Save Settings and Reboot Device">\n')
    await response.send('</form>\n')
    await response.send('</body></html>\n')


def run_server():
    app.run(host='0.0.0.0', port=80)


def test_thread():
    # Real payload will be here
    # Now t is just placeholder
    i = 1
    while True:
        print("test_thread {}".format(i))
        utime.sleep(10)
        i = i + 1


def start_thread():
    # Just placeholder for testing
    _thread.start_new_thread(test_thread, ())


@app.route('/static/<file_name>')
async def images(req, resp, fn):
    # Filename - in parameter
    # This endpoint is used for css files
    # and will be used for js/images etc.
    await resp.send_file('wwwroot/{}'.format(file_name))

# Rest API resources
app.add_resource(Config, '/api/v1/config')
app.add_resource(Reset, '/api/v1/reset')
app.add_resource(FileSystem, '/api/v1/fs/<file_name>')

start_thread()
run_server()
