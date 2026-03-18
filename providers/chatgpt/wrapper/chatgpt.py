from . import Log, Utils, Headers, Challenges, VM, IP_Info
from random       import randint, random, choice
from zoneinfo     import ZoneInfo
from curl_cffi    import requests
from datetime     import datetime
from uuid         import uuid4
from json         import loads
from time         import time
from typing       import Any
from base64       import b64decode
from PIL import Image
from io import BytesIO


class ChatGPT:
    
    
    def __init__(self, proxy: str=None, cookies: dict = None) -> Any:
        self.session: requests.session.Session = requests.Session(impersonate="chrome133a")
        self.session.headers = Headers.DEFAULT
        self.data: dict = {}
        
        if proxy:
            
            self.session.proxies = {
                "all": proxy
            }
            
        self.ip_info: list = IP_Info.fetch_info(self.session)
        self.timezone_offset: int = int(datetime.now(ZoneInfo(self.ip_info[5])).utcoffset().total_seconds() / 60)
        self.reacts: list = [
            "location",
            "__reactContainer$" + self._generate_react(),
            "_reactListening" + self._generate_react(),
        ]
        self.window_keys: list = [
            "0",
            "window",
            "self",
            "document",
            "name",
            "location",
            "customElements",
            "history",
            "navigation",
            "locationbar",
            "menubar",
            "personalbar",
            "scrollbars",
            "statusbar",
            "toolbar",
            "status",
            "closed",
            "frames",
            "length",
            "top",
            "opener",
            "parent",
            "frameElement",
            "navigator",
            "origin",
            "external",
            "screen",
            "innerWidth",
            "innerHeight",
            "scrollX",
            "pageXOffset",
            "scrollY",
            "pageYOffset",
            "visualViewport",
            "screenX",
            "screenY",
            "outerWidth",
            "outerHeight",
            "devicePixelRatio",
            "event",
            "clientInformation",
            "screenLeft",
            "screenTop",
            "styleMedia",
            "onsearch",
            "trustedTypes",
            "performance",
            "onappinstalled",
            "onbeforeinstallprompt",
            "crypto",
            "indexedDB",
            "sessionStorage",
            "localStorage",
            "onbeforexrselect",
            "onabort",
            "onbeforeinput",
            "onbeforematch",
            "onbeforetoggle",
            "onblur",
            "oncancel",
            "oncanplay",
            "oncanplaythrough",
            "onchange",
            "onclick",
            "onclose",
            "oncontentvisibilityautostatechange",
            "oncontextlost",
            "oncontextmenu",
            "oncontextrestored",
            "oncuechange",
            "ondblclick",
            "ondrag",
            "ondragend",
            "ondragenter",
            "ondragleave",
            "ondragover",
            "ondragstart",
            "ondrop",
            "ondurationchange",
            "onemptied",
            "onended",
            "onerror",
            "onfocus",
            "onformdata",
            "oninput",
            "oninvalid",
            "onkeydown",
            "onkeypress",
            "onkeyup",
            "onload",
            "onloadeddata",
            "onloadedmetadata",
            "onloadstart",
            "onmousedown",
            "onmouseenter",
            "onmouseleave",
            "onmousemove",
            "onmouseout",
            "onmouseover",
            "onmouseup",
            "onmousewheel",
            "onpause",
            "onplay",
            "onplaying",
            "onprogress",
            "onratechange",
            "onreset",
            "onresize",
            "onscroll",
            "onsecuritypolicyviolation",
            "onseeked",
            "onseeking",
            "onselect",
            "onslotchange",
            "onstalled",
            "onsubmit",
            "onsuspend",
            "ontimeupdate",
            "ontoggle",
            "onvolumechange",
            "onwaiting",
            "onwebkitanimationend",
            "onwebkitanimationiteration",
            "onwebkitanimationstart",
            "onwebkittransitionend",
            "onwheel",
            "onauxclick",
            "ongotpointercapture",
            "onlostpointercapture",
            "onpointerdown",
            "onpointermove",
            "onpointerrawupdate",
            "onpointerup",
            "onpointercancel",
            "onpointerover",
            "onpointerout",
            "onpointerenter",
            "onpointerleave",
            "onselectstart",
            "onselectionchange",
            "onanimationend",
            "onanimationiteration",
            "onanimationstart",
            "ontransitionrun",
            "ontransitionstart",
            "ontransitionend",
            "ontransitioncancel",
            "onafterprint",
            "onbeforeprint",
            "onbeforeunload",
            "onhashchange",
            "onlanguagechange",
            "onmessage",
            "onmessageerror",
            "onoffline",
            "ononline",
            "onpagehide",
            "onpageshow",
            "onpopstate",
            "onrejectionhandled",
            "onstorage",
            "onunhandledrejection",
            "onunload",
            "isSecureContext",
            "crossOriginIsolated",
            "scheduler",
            "alert",
            "atob",
            "blur",
            "btoa",
            "cancelAnimationFrame",
            "cancelIdleCallback",
            "captureEvents",
            "clearInterval",
            "clearTimeout",
            "close",
            "confirm",
            "createImageBitmap",
            "fetch",
            "find",
            "focus",
            "getComputedStyle",
            "getSelection",
            "matchMedia",
            "moveBy",
            "moveTo",
            "open",
            "postMessage",
            "print",
            "prompt",
            "queueMicrotask",
            "releaseEvents",
            "reportError",
            "requestAnimationFrame",
            "requestIdleCallback",
            "resizeBy",
            "resizeTo",
            "scroll",
            "scrollBy",
            "scrollTo",
            "setInterval",
            "setTimeout",
            "stop",
            "structuredClone",
            "webkitCancelAnimationFrame",
            "webkitRequestAnimationFrame",
            "chrome",
            "caches",
            "cookieStore",
            "ondevicemotion",
            "ondeviceorientation",
            "ondeviceorientationabsolute",
            "sharedStorage",
            "documentPictureInPicture",
            "fetchLater",
            "getScreenDetails",
            "queryLocalFonts",
            "showDirectoryPicker",
            "showOpenFilePicker",
            "showSaveFilePicker",
            "originAgentCluster",
            "viewport",
            "onpageswap",
            "onpagereveal",
            "credentialless",
            "fence",
            "launchQueue",
            "speechSynthesis",
            "oncommand",
            "onscrollend",
            "onscrollsnapchange",
            "onscrollsnapchanging",
            "webkitRequestFileSystem",
            "webkitResolveLocalFileSystemURL",
            "define",
            "ethereum",
            "__oai_SSR_HTML",
            "__reactRouterContext",
            "$RC",
            "__oai_SSR_TTI",
            "__reactRouterManifest",
            "__reactRouterVersion",
            "DD_RUM",
            "__REACT_INTL_CONTEXT__",
            "regeneratorRuntime",
            "DD_LOGS",
            "__STATSIG__",
            "__mobxInstanceCount",
            "__mobxGlobals",
            "_g",
            "__reactRouterRouteModules",
            "__SEGMENT_INSPECTOR__",
            "__reactRouterDataRouter",
            "MotionIsMounted",
            "_oaiHandleSessionExpired"
        ]
        
        if not cookies:
            self._fetch_cookies()
        else:
            self.session.cookies.update(cookies)
            
    def _generate_react(self) -> str:
        n = random() 
        base36 = ''
        chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        x = int(n * 36**10)
        for _ in range(10):
            x, r = divmod(x, 36)
            base36 = chars[r] + base36
        return base36
    
    def _parse_event_stream(self, stream_data: str) -> str:
        result: list = []
        
        events = stream_data.strip().split('\n\n')
        
        for event in events:
            data_parts = []
            for line in event.split('\n'):
                if line.startswith('data:'):
                    data_parts.append(line[5:].strip())
                elif data_parts:
                    data_parts[-1] += '\n' + line
            
            if not data_parts:
                continue
                
            data_str = '\n'.join(data_parts)
            
            if data_str == '[DONE]':
                break
            
            try:
                data: dict = loads(data_str)
            except Exception:
                continue
            
            if not isinstance(data, dict):
                continue

            if data.get('o') == 'append' and data.get('p') == '/message/content/parts/0':
                result.append(data.get('v'))
            
            elif isinstance(data.get('v'), list):
                for op in data['v']:
                    if isinstance(op, dict) and op.get('o') == 'append' and op.get('p') == '/message/content/parts/0':
                        result.append(op.get('v'))
            
            elif 'v' in data and isinstance(data['v'], str):
                result.append(data['v'])
                    
        return ''.join(result)

    def _stream_conversation_live(self, url: str, json_data: dict):
        response = self.session.post(url, json=json_data, stream=True)
        self.session.cookies.update(response.cookies)

        buffer = ""
        full_response_parts = []

        for raw_chunk in response.iter_content():
            if not raw_chunk:
                continue
            buffer += raw_chunk.decode('utf-8', errors='replace')

            while '\n\n' in buffer:
                event_str, buffer = buffer.split('\n\n', 1)

                for line in event_str.split('\n'):
                    if not line.startswith('data:'):
                        continue
                    data_str = line[5:].strip()
                    if data_str == '[DONE]':
                        break

                    try:
                        data = loads(data_str)
                    except Exception:
                        continue

                    if not isinstance(data, dict):
                        continue

                    if isinstance(data.get('v'), dict):
                        v = data['v']
                        if 'conversation_id' in v and 'conversation_id' not in self.data:
                            self.data["conversation_id"] = v["conversation_id"]
                        msg = v.get('message', {})
                        if msg.get('id') and msg.get('author', {}).get('role') == 'assistant':
                            self.data["parent_message_id"] = msg['id']

                    ops = []
                    if data.get('o') == 'append' and data.get('p') == '/message/content/parts/0':
                        ops = [data]
                    elif isinstance(data.get('v'), list):
                        ops = data['v']
                    elif data.get('o') == 'patch' and isinstance(data.get('v'), list):
                        ops = data['v']

                    for op in ops:
                        if isinstance(op, dict) and op.get('o') == 'append' and op.get('p') == '/message/content/parts/0':
                            token = op.get('v', '')
                            if token:
                                full_response_parts.append(token)
                                yield token

        self.response = ''.join(full_response_parts)

    def start_conversation_stream(self, message: str, model: str = 'auto'):
        self._get_tokens()
        conduit_token: str = self.get_conduit(model=model)

        time_1: int = randint(6000, 9000)
        proof_token: str = Challenges.solve_pow(self.data["proofofwork"]["seed"], self.data["proofofwork"]["difficulty"], self.data["config"])
        Log.Success(f"Solved POW: {proof_token}")
        turnstile_token: str = VM.get_turnstile(self.data["bytecode"], self.data["vm_token"], str(self.ip_info[:-1]))

        self.session.headers = Headers.CONVERSATION
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
            'oai-echo-logs': f'0,{time_1},1,{time_1 + randint(1000, 1200)}',
            'openai-sentinel-chat-requirements-token': self.data["token"],
            'openai-sentinel-proof-token': proof_token,
            'openai-sentinel-turnstile-token': turnstile_token,
            'x-conduit-token': conduit_token,
        })

        conversation_data: dict = {
            'action': 'next',
            'messages': [
                {
                    'id': str(uuid4()),
                    'author': { 'role': 'user' },
                    'create_time': round(time(), 3),
                    'content': { 'content_type': 'text', 'parts': [message] },
                    'metadata': {
                        'selected_github_repos': [],
                        'selected_all_github_repos': False,
                        'serialization_metadata': { 'custom_symbol_offsets': [] },
                    },
                },
            ],
            'parent_message_id': 'client-created-root',
            'model': model,
            'timezone_offset_min': self.timezone_offset,
            'timezone': self.ip_info[5],
            'history_and_training_disabled': True,
            'conversation_mode': { 'kind': 'primary_assistant' },
            'enable_message_followups': True,
            'system_hints': [],
            'supports_buffering': True,
            'supported_encodings': ['v1'],
            'client_contextual_info': {
                'is_dark_mode': True,
                'time_since_loaded': randint(3, 6),
                'page_height': 1219, 'page_width': 3440,
                'pixel_ratio': 1, 'screen_height': 1440, 'screen_width': 3440,
            },
            'paragen_cot_summary_display_override': 'allow',
            'force_parallel_switch': 'auto',
        }

        yield from self._stream_conversation_live('https://chatgpt.com/backend-anon/f/conversation', conversation_data)

    def ask_question_stream(self, message: str, model: str = 'auto'):
        yield from self.start_conversation_stream(message, model=model)

    def ask_question(self, message: str, image: str = None, model: str = 'auto') -> str:
        
        if not image:
            self.start_conversation(message, model=model)
        else:
            self.start_with_image(message, image, model=model)
        
        return self.response

    def _fetch_cookies(self) -> None:
        
        load_site: requests.models.Response = self.session.get("https://chatgpt.com")
        self.session.cookies.update(load_site.cookies)

        self.data["prod"] = load_site.text.split('data-build="')[1].split('"')[0]
        self.data["device-id"] = self.session.cookies.get("oai-did")
        
        self.start_time: int = int(time() * 1000)
        self.sid: str = str(uuid4())
        
        self.data["config"] = [
            4880,
            datetime.now(ZoneInfo(self.ip_info[5])).strftime(f"%a %b %d %Y %H:%M:%S GMT%z ({datetime.now(ZoneInfo(self.ip_info[5])).tzname()})"),
            4294705152,
            random(),
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            None,
            self.data["prod"],
            "de-DE",
            "de-DE,de,en-US,en",
            random(),
            "webkitGetUserMedia-function webkitGetUserMedia() { [native code] }",
            choice(self.reacts),
            choice(self.window_keys),
            randint(800, 1400) + random(),
            self.sid,
            "",
            20,
            self.start_time
        ]
    
    def _get_tokens(self, process_time: int=randint(1400, 2000)) -> None:
        
        self.session.headers = Headers.REQUIREMENTS
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
        })
        
        p_value: str = Challenges.generate_token(self.data["config"])
        self.data["vm_token"] = p_value
        
        self.data["config"] = [
            4880,
            datetime.now(ZoneInfo(self.ip_info[5])).strftime(f"%a %b %d %Y %H:%M:%S GMT%z ({datetime.now(ZoneInfo(self.ip_info[5])).tzname()})"),
            4294705152,
            random(),
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            None,
            self.data["prod"],
            "de-DE",
            "de-DE,de,en-US,en",
            random(),
            "webkitGetUserMedia-function webkitGetUserMedia() { [native code] }",
            choice(self.reacts),
            choice(self.window_keys),
            process_time + random(),
            self.sid,
            "",
            20,
            self.start_time
        ]
        
        requirements_data: dict = {
            'p': p_value,
        }
        
        requirements_request: requests.models.Response = self.session.post('https://chatgpt.com/backend-anon/sentinel/chat-requirements', json=requirements_data)

        if requirements_request.status_code == 200:
            self.data["token"] = requirements_request.json().get("token")
            self.data["proofofwork"] = requirements_request.json().get("proofofwork")
            self.data["bytecode"] = requirements_request.json().get("turnstile").get("dx")
        
        else:
            Log.Error("Something went wrong while fetching chat requirements")
    
    def get_conduit(self, next: bool = False, model: str = 'auto') -> str:
        self.session.headers = Headers.CONDUIT
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
        })
        
        if not next:
            post_data: dict = {
                'action': 'next',
                'fork_from_shared_post': False,
                'parent_message_id': 'client-created-root',
                'model': model,
                'timezone_offset_min': self.timezone_offset,
                'timezone': self.ip_info[5],
                'history_and_training_disabled': True,
                'conversation_mode': {
                    'kind': 'primary_assistant',
                },
                'system_hints': [],
                'supports_buffering': True,
                'supported_encodings': [
                    'v1',
                ],
            }
        
        else:
            post_data: dict = {
                'action': 'next',
                'fork_from_shared_post': False,
                'conversation_id': self.data["conversation_id"],
                'parent_message_id': self.data["parent_message_id"],
                'model': model,
                'timezone_offset_min': self.timezone_offset,
                'timezone': self.ip_info[5],
                'history_and_training_disabled': True,
                'conversation_mode': {
                    'kind': 'primary_assistant',
                },
                'system_hints': [],
                'supports_buffering': True,
                'supported_encodings': [
                    'v1',
                ],
            }
                    
        conduit_request: requests.models.Response = self.session.post('https://chatgpt.com/backend-anon/f/conversation/prepare', json=post_data)
        
        if '"status":"ok"' in conduit_request.text:
            return conduit_request.json().get("conduit_token")
        
        else:
            Log.Error("Something went wrong while fetching conduit token: ")
            Log.Error(conduit_request.text)
            return None
    
    def start_conversation(self, message: str, model: str = 'auto') -> None:
        for _ in self.start_conversation_stream(message, model=model):
            pass

    def upload_image(self, image: str) -> None:
        
        self.session.headers = Headers.REQUIREMENTS
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
        })
        
        self.file_name: str = str(uuid4())
        
        if image.startswith("data:image"):
            image = image.split(",")[1]
            
        self.file_size: int = len(b64decode(image))
        self.width, self.height = Image.open(BytesIO(b64decode(image))).size
        
        image_data: dict = {
            'file_name': f'{self.file_name}.png',
            'file_size': self.file_size,
            'use_case': 'multimodal',
            'timezone_offset_min': self.timezone_offset,
            'reset_rate_limits': False,
        }
        file_request: requests.models.Response = self.session.post('https://chatgpt.com/backend-anon/files', json=image_data)
        
        self.data["file_id"] = file_request.json().get("file_id")
        upload_url: str = file_request.json().get("upload_url")
        
        self.session.headers = Headers.FILE
        upload_request: requests.models.Response = self.session.put(upload_url, data=b64decode(image))

        self.session.headers = Headers.REQUIREMENTS
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
        })
        
        process_data: dict = {
            'file_id': self.data["file_id"],
            'use_case': 'multimodal',
            'index_for_retrieval': False,
            'file_name': f'{self.file_name}.png',
        }
        
        process_request: requests.models.Response = self.session.post('https://chatgpt.com/backend-anon/files/process_upload_stream', json=process_data)
        
        if "Succeeded processing " in process_request.text:
            return
        else:
            Log.Error("Something went wrong while uploading image")
        
    def start_with_image(self, message: str, image: str, model: str = 'auto') -> None:
        
        self._get_tokens()
        conduit_token: str = self.get_conduit(model=model)
        self.upload_image(image)
        
        time_1: int = randint(6000, 9000)
        proof_token: str = Challenges.solve_pow(self.data["proofofwork"]["seed"], self.data["proofofwork"]["difficulty"], self.data["config"])
        
        turnstile_token: str = VM.get_turnstile(self.data["bytecode"], self.data["vm_token"], str(self.ip_info[:-1]))

        self.session.headers = Headers.CONVERSATION
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
            'oai-echo-logs': f'0,{time_1},1,{time_1 + randint(1000, 1200)}',
            'openai-sentinel-chat-requirements-token': self.data["token"],
            'openai-sentinel-proof-token': proof_token,
            'openai-sentinel-turnstile-token': turnstile_token,
            'x-conduit-token': conduit_token,
        })

        conversation_data: dict = {
            'action': 'next',
            'messages': [
                {
                    'id': str(uuid4()),
                    'author': {
                        'role': 'user',
                    },
                    'create_time': round(time(), 3),
                    'content': {
                        'content_type': 'multimodal_text',
                        'parts': [
                            {
                                'content_type': 'image_asset_pointer',
                                'asset_pointer': f'file-service://{self.data["file_id"]}',
                                'size_bytes': self.file_size,
                                'width': self.width,
                                'height': self.height,
                            },
                            message,
                        ],
                    },
                    'metadata': {
                        'attachments': [
                            {
                                'id': self.data["file_id"],
                                'size': self.file_size,
                                'name': f'{self.file_name}.png',
                                'mime_type': 'image/png',
                                'width': self.width,
                                'height': self.height,
                                'source': 'local',
                            },
                        ],
                        'selected_github_repos': [],
                        'selected_all_github_repos': False,
                        'serialization_metadata': {
                            'custom_symbol_offsets': [],
                        },
                    },
                },
            ],
            'parent_message_id': 'client-created-root',
            'model': model,
            'timezone_offset_min': self.timezone_offset,
            'timezone': self.ip_info[5],
            'history_and_training_disabled': True,
            'conversation_mode': {
                'kind': 'primary_assistant',
            },
            'enable_message_followups': True,
            'system_hints': [],
            'supports_buffering': True,
            'supported_encodings': [
                'v1',
            ],
            'client_contextual_info': {
                'is_dark_mode': True,
                'time_since_loaded': randint(3, 6),
                'page_height': 1219,
                'page_width': 3440,
                'pixel_ratio': 1,
                'screen_height': 1440,
                'screen_width': 3440,
            },
            'paragen_cot_summary_display_override': 'allow',
            'force_parallel_switch': 'auto',
        }
        
        for _ in self._stream_conversation_live('https://chatgpt.com/backend-anon/f/conversation', conversation_data):
            pass
    
    def hold_conversation(self, message: str, new: bool = True, model: str = 'auto') -> None:
        self.index = 2000
        
        if new:
            self.start_conversation(message, model=model)
        
        conduit_token: str = self.get_conduit(next=True, model=model)
        
        self._get_tokens(randint(self.index, self.index + 1000))
        self.index += 3000
        
        time_1: int = randint(self.index, self.index + 3000)
        proof_token: str = Challenges.solve_pow(self.data["proofofwork"]["seed"], self.data["proofofwork"]["difficulty"], self.data["config"])
        
        turnstile_token: str = VM.get_turnstile(self.data["bytecode"], self.data["vm_token"], str(self.ip_info[:-1]))


        self.session.headers = Headers.CONVERSATION
        self.session.headers.update({
            'oai-client-version': self.data["prod"],
            'oai-device-id': self.data["device-id"],
            'oai-echo-logs': f'0,{time_1},1,{time_1 + randint(1000, 1200)}',
            'openai-sentinel-chat-requirements-token': self.data["token"],
            'openai-sentinel-proof-token': proof_token,
            'openai-sentinel-turnstile-token': turnstile_token,
            'x-conduit-token': conduit_token,
        })
        
        if new:
            new_message: str = input("Prompt: ")
        else:
            new_message: str = message
        
        conversation_data: dict = {
            'action': 'next',
            'messages': [
                {
                    'id': str(uuid4()),
                    'author': {
                        'role': 'user',
                    },
                    'create_time': round(time(), 3),
                    'content': {
                        'content_type': 'text',
                        'parts': [
                            new_message,
                        ],
                    },
                    'metadata': {
                        'selected_github_repos': [],
                        'selected_all_github_repos': False,
                        'serialization_metadata': {
                            'custom_symbol_offsets': [],
                        },
                    },
                },
            ],
            'conversation_id': self.data["conversation_id"],
            'parent_message_id': self.data["parent_message_id"],
            'model': 'auto',
            'timezone_offset_min': self.timezone_offset,
            'timezone': self.ip_info[5],
            'history_and_training_disabled': True,
            'conversation_mode': {
                'kind': 'primary_assistant',
            },
            'enable_message_followups': True,
            'system_hints': [],
            'supports_buffering': True,
            'supported_encodings': [
                'v1',
            ],
            'client_contextual_info': {
                'is_dark_mode': True,
                'time_since_loaded': 17,
                'page_height': 1219,
                'page_width': 3440,
                'pixel_ratio': 1,
                'screen_height': 1440,
                'screen_width': 3440,
            },
            'paragen_cot_summary_display_override': 'allow',
            'force_parallel_switch': 'auto',
        }
        
        for _ in self._stream_conversation_live('https://chatgpt.com/backend-anon/f/conversation', conversation_data):
            pass
