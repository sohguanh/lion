import http.server as httpServer
import http.client as httpClient

import util.http as httpUtil
import util.template as templateUtil
import util.i18n as i18nUtil


class MyCompanyChainHandler(httpUtil.Handler):
    def __init__(self):
        pass

    def handle(self, obj: httpServer.BaseHTTPRequestHandler) -> bool:
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/html; charset=utf-8')
        obj.end_headers()
        obj.wfile.write(bytearray(self.chain_name, 'utf-8'))
        tpl = templateUtil.get_template("helloworld")
        if tpl is not None:
            rb_en_US = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("en", "US"))
            rb_zh_CN = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("zh", "CN"))
            rb_zh_TW = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("zh", "TW"))
            param = {
                'Title': 'Lion',
                'Greeting1': rb_en_US['how.are.you'],
                'Greeting2': rb_zh_CN['how.are.you'],
                'Greeting3': rb_zh_TW['how.are.you'],
                'SpecialDate1': rb_en_US['special.date'].format('03', 12, 1974),
                'SpecialDate2': rb_zh_CN['special.date'].format(1974, 12, '03'),
                'SpecialDate3': rb_zh_TW['special.date'].format(1974, 12, '03')
            }
            obj.wfile.write(bytearray(tpl.safe_substitute(param), 'utf-8'))
        return self.ret
