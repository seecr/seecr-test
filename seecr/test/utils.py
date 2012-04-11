
    _scriptTagRegex = compile("<script[\s>].*?</script>", DOTALL)
    _entities = {
        '&nbsp;': ' ',
        '&ndash;': "&#8211;",
        '&mdash;': "&#8212;",
        '&lsquo;': "‘",
        '&rsquo;': "’",
        '&larr;': "&lt;-",
    }
    
    def parseHtmlAsXml(self, body):
        def forceXml(body):
            newBody = body
            for entity, replacement in self._entities.items():
                newBody = newBody.replace(entity, replacement)
            newBody = self._scriptTagRegex.sub('', newBody)
            return newBody
        try: 
            return parse(StringIO(forceXml(body)))
        except XMLSyntaxError:
            print body 
            raise

    def getPage(self, port, path, arguments=None, expectedStatus="200"):
        additionalHeaders = {}
        if self.sessionId:
            additionalHeaders['Cookie'] = 'session=' + self.sessionId
        header, body = getRequest(port, path, arguments, parse=False, additionalHeaders=additionalHeaders)
        self.assertHttpOK(header, body, expectedStatus=expectedStatus)
        return header, body

    def postToPage(self, port, path, data, expectedStatus="302"):
        additionalHeaders = {}
        if self.sessionId:
            additionalHeaders['Cookie'] = 'session=' + self.sessionId
        postBody = urlencode(data, doseq=True)
        header, body = postRequest(port, path, data=postBody, contentType='application/x-www-form-urlencoded', parse=False, additionalHeaders=additionalHeaders)
        self.assertHttpOK(header, body, expectedStatus=expectedStatus)
        return header, body 

    def assertHttpOK(self, header, body, expectedStatus="200"):
        try:
            self.assertSubstring("HTTP/1.0 %s" % expectedStatus, header)
            self.assertNotSubstring("Traceback", header + "\r\n\r\n" + body)
        except AssertionError, e:
            print header, body
            raise

    def assertSubstring(self, value, s):
        if not value in s:
            raise AssertionError("assertSubstring fails: %s must occur in %s" % (value, s))

    def assertNotSubstring(self, value, s):
        if value in s:
            raise AssertionError("assertNotSubstring fails: %s must not occur in %s" % (value, s))
