#---------------------------------------------------------------------------
# Logging Extensions
#---------------------------------------------------------------------------

from io import StringIO
import logging

class Formatter(logging.Formatter):
    def format(self, record):
        out = StringIO()
        out.write(self.formatTime(record))
        out.write(" {:5}.".format(record.process))
        thread = record.threadName.replace("Thread", "").replace("Dummy-", "")
        out.write("{:5}".format(thread))
        out.write("{:7.7} ".format(record.levelname))
        name = record.name
        if name.startswith("davezdominoes."):
            name = name[14:]
        out.write("{:26}: ".format(name))
        out.write(record.getMessage())

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            out.write("\n{0.exc_text}".format(record))
        if record.stack_info:
            out.write("\n{}".format(self.formatStack(record.stack_info)))

        return out.getvalue()

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            try:
                msg = msg % self.args
            except TypeError:
                msg = msg.format(self.args)
        return msg

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

