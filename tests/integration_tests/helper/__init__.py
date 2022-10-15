from datetime import datetime
import json

import pytz

from core.helpers import request_processor, own_json

def process_and_add_slfs(request):
    request['lt'] = datetime.now(tz=pytz.utc)
    output = json.loads(own_json.dumps(request))
    output['slfs'] = request_processor.calculate_slfs(output)

    return output