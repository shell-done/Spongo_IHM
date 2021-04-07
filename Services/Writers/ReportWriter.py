from Models.Analysis import Analysis

class ReportWriter():
    def __init__(self, analysis: Analysis):
        self._analysis = analysis

    def text(self) -> str:
        return None

    def checkErrors(self) -> str:
        return None

    def write(self, filepath: str):
        return None

    def toHTML(self, text, truncate = True):
        if truncate:
            threshold = 10000
            lines = text.split("\n")
            if len(lines) > threshold:
                lines = lines[:threshold]
                lines.append("")
                lines.append("<p style='text-align: center; font-weight: bold;'>Aperçu tronqué aux %d premières lignes.</p>" % threshold)
                lines.append("")
                text = "\n".join(lines)

        return """
        <html>
            <head>
                <meta charset='utf-8'>
            </head>
            <body>
                <pre>%s</pre>
            </body>
        </html>
        """ % text
    