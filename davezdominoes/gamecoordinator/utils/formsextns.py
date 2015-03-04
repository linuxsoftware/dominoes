#---------------------------------------------------------------------------
# Various extensions to use with WTForms
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# A WTForms2/Pyramid CSRF plugin
# Based originally on https://bitbucket.org/evannook/pyramid_wtforms
#---------------------------------------------------------------------------
from wtforms.form import Form
from wtforms.csrf.core import CSRF
from pyramid.threadlocal import get_current_request
from contextlib import suppress

class PyramidCsrf(CSRF):
    "This class uses pyramid builtin csrf facility."
    def generate_csrf_token(self, csrf_token):
        # XXX: I know this is not the best way to get the session, but I
        # don't want to have to pass in the request object
        request = get_current_request()
        if request:
            return request.session.get_csrf_token()

    def validate_csrf_token(self, form, field):
        if field.current_token != field.data:
            form.meta.csrf_handler()

    @staticmethod
    def handleCsrf():
        raise ValidationError('Invalid CSRF Token')

class SecureForm(Form):
    "Form class which enables csrf protection"
    class Meta:
        csrf = True
        csrf_field_name = "csrfToken"
        csrf_class = PyramidCsrf
        csrf_handler = staticmethod(PyramidCsrf.handleCsrf)


#---------------------------------------------------------------------------
# Disabled/ablable versions of the fields
#---------------------------------------------------------------------------
#from wtforms import Form
from wtforms import fields

def DisabledFieldFactory(Base):
    def my_init(self, *args, **kwargs):
        self.disabled = kwargs.pop('disabled', True)
        Base.__init__(self, *args, **kwargs)
    def my_call(self, *args, **kwargs):
        if self.disabled:
            kwargs.setdefault("disabled", True)
        return Base.__call__(self, *args, **kwargs)
    def my_populate_obj(self, *args, **kwargs):
        if not self.disabled:
            Base.populate_obj(self, *args, **kwargs)
    def my_process_formdata(self, *args, **kwargs):
        if not self.disabled:
            Base.process_formdata(self, *args, **kwargs)
    def my_Option(self, *args, **kwargs):
        DisabledOption = DisabledFieldFactory(fields.SelectFieldBase._Option)
        kwargs["disabled"] = self.disabled
        return DisabledOption(*args, **kwargs)
    Field = type("Disablable" + Base.__name__, (Base,),
                 {'__init__':         my_init,
                  '__call__':         my_call,
                  'process_formdata': my_process_formdata,
                  'populate_obj':     my_populate_obj})
    if issubclass(Base, fields.SelectFieldBase):
        Field._Option = my_Option
    return Field

DisabledBooleanField         = DisabledFieldFactory(fields.BooleanField)
DisabledDecimalField         = DisabledFieldFactory(fields.DecimalField)
DisabledDateField            = DisabledFieldFactory(fields.DateField)
DisabledDateTimeField        = DisabledFieldFactory(fields.DateTimeField)
DisabledFieldList            = DisabledFieldFactory(fields.FieldList)
DisabledFloatField           = DisabledFieldFactory(fields.FloatField)
DisabledFormField            = DisabledFieldFactory(fields.FormField)
DisabledIntegerField         = DisabledFieldFactory(fields.IntegerField)
DisabledRadioField           = DisabledFieldFactory(fields.RadioField)
DisabledSelectField          = DisabledFieldFactory(fields.SelectField)
DisabledSelectMultipleField  = DisabledFieldFactory(fields.SelectMultipleField)
DisabledStringField          = DisabledFieldFactory(fields.StringField)
DisabledTextAreaField        = DisabledFieldFactory(fields.TextAreaField)
DisabledPasswordField        = DisabledFieldFactory(fields.PasswordField)
DisabledFileField            = DisabledFieldFactory(fields.FileField)
DisabledHiddenField          = DisabledFieldFactory(fields.HiddenField)
DisabledSubmitField          = DisabledFieldFactory(fields.SubmitField)
DisabledTextField            = DisabledFieldFactory(fields.TextField)

#---------------------------------------------------------------------------
# Standard Submit Buttons
#---------------------------------------------------------------------------
from wtforms.fields  import HiddenField
from wtforms.fields  import SubmitField

class SubmitBtns(Form):
    class Meta:
        csrf = True
        csrf_field_name = "csrfToken"
        csrf_class = PyramidCsrf
        csrf_handler = staticmethod(PyramidCsrf.handleCsrf)

    rowid       = HiddenField()
    hiddenBtn   = SubmitField("  ")
    addBtn      = DisabledSubmitField("Add",             disabled=False)
    delBtn      = DisabledSubmitField("Delete",          disabled=False)
    modBtn      = DisabledSubmitField("Modify",          disabled=False)
    cancelBtn   = DisabledSubmitField("Cancel",          disabled=False)
    okBtn       = DisabledSubmitField("OK",              disabled=False)
    anotherBtn  = DisabledSubmitField("OK+Another",      disabled=False)
    misc1Btn    = DisabledSubmitField("Miscellany",      disabled=False)
    misc2Btn    = DisabledSubmitField("Miscellany",      disabled=False)


#---------------------------------------------------------------------------
# Coerce functions - useful for SelectFields
#---------------------------------------------------------------------------
def toIdOf(cls):
    def toId(obj):
        if isinstance(obj, cls):
            return obj.id
        else:
            return obj
    return toId

def toIntIdOf(cls):
    def toId(obj):
        if isinstance(obj, cls):
            return int(obj.id)
        else:
            return int(obj)
    return toId

#---------------------------------------------------------------------------
# Pyramid Form with Buttons
#---------------------------------------------------------------------------
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotImplemented
from sqlalchemy import inspect as sqla_inspect
#TODO inherit from ModelForm?
#from wtforms_alchemy import ModelForm

class PyramidForm(Form):
    def __init__(self, obj=None, prefix='', **kwargs):
        super().__init__(prefix=prefix, **kwargs)
        self.btns = SubmitBtns(prefix=prefix,
                               meta={'csrf_handler': self.handleCsrf},
                               **kwargs)
        self.obj = self._obj = obj
        self.okUrl      = \
        self.cancelUrl  = \
        self.anotherUrl = \
        self.addUrl     = \
        self.misc1Url   = \
        self.misc2Url   = \
        self.modUrl     = None

        for field in self._fields.values():
            field.extattrs = {}

    def handle(self, request, info={}):
        retval = dict(info)
        retval['form'] = self
        retval['btns'] = self.btns
        self.process(request.POST, self.obj)
        if request.method == 'POST':
            self.btns.process(request.POST)
            if self.btns.cancelBtn.data:
                self.checkCsrf()
                return self.handleCancel(request, retval)
            elif self.btns.okBtn.data or self.btns.anotherBtn.data:
                self.checkCsrf()
                if self.validate():
                    if self.btns.anotherBtn.data:
                        return self.handleAnother(request, retval)
                    else:
                        return self.handleOk(request, retval)
                else:
                    return retval
            elif self.btns.addBtn.data:
                self.checkCsrf()
                return self.handleAdd(request, retval)
            elif self.btns.delBtn.data:
                self.checkCsrf()
                return self.handleDel(request, retval)
            elif self.btns.modBtn.data:
                self.checkCsrf()
                return self.handleMod(request, retval)
            elif self.btns.misc1Btn.data:
                self.checkCsrf()
                return self.handleMisc1(request, retval)
            elif self.btns.misc2Btn.data:
                self.checkCsrf()
                return self.handleMisc2(request, retval)
            elif self.btns.hiddenBtn.data:
                pass # swallow this as default
            else:
                return self.handleNotImplemented(retval)
        return retval

    def handleCancel(self, request, retval):
        return HTTPFound(location = self.cancelUrl or request.path_url)

    def handleOk(self, request, retval):
        if self.obj:
            self.populate_obj(self.obj)
            self.save()
        return HTTPFound(location = self.okUrl or request.path_url)

    def handleAnother(self, request, retval):
        retval = self.handleOk(request, retval)
        if isinstance(retval, HTTPFound):
            retval.location = self.anotherUrl or request.path_url
        return retval

    def handleAdd(self, request, retval):
        return self._redirectTo(self.addUrl, retval)

    def handleDel(self, request, retval):
        return self.handleNotImplemented(retval)

    def handleMod(self, request, retval):
        return self._redirectTo(self.modUrl, retval)

    def handleMisc1(self, request, retval):
        return self._redirectTo(self.misc1Url, retval)

    def handleMisc2(self, request, retval):
        return self._redirectTo(self.misc2Url, retval)

    def _redirectTo(self, url, retval):
        if url:
            return HTTPFound(location = url)
        else:
            return self.handleNotImplemented(retval)

    def save(self):
        ormObj = sqla_inspect(self.obj, raiseerr=False)
        if ormObj and ormObj.transient:
            self.obj.insert()

    def checkCsrf(self):
        self.btns.validate()

    def handleCsrf(self):
        raise HTTPForbidden()

    def handleNotImplemented(self, retval):
        raise HTTPNotImplemented()

#---------------------------------------------------------------------------
# Custom Validators
#---------------------------------------------------------------------------
from wtforms import validators
from wtforms.validators import ValidationError
from cgi import FieldStorage

class DataRequiredIf(validators.DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value
    # from http://stackoverflow.com/questions/8463209
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(DataRequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(DataRequiredIf, self).__call__(form, field)


class FileIsPdf(object):
    """
    Checks that the file being uploaded is a PDF
    """
    def __call__(self, form, field):
        if (not hasattr(field.data, "filename") or
            not hasattr(field.data, "file")):
            raise ValidationError("Is not a file field")
        if field.data.filename[-4:].lower() != ".pdf":
            raise ValidationError("Upload .PDF files only")
        fp = field.data.file
        fp.seek(0)
        header = fp.read(5)
        if header != b"%PDF-":
            # 99% of PDFs start with %PDF-1, but it may be further in
            fp.seek(0)
            header = fp.read(1024)
            if b"%PDF-" not in header:
                raise ValidationError("Corrupt file or not a PDF file")
        fp.seek(-10, 2)
        trailer = fp.read(10)
        if b"%%EOF" not in trailer:
            raise ValidationError("Corrupt file or not a PDF file")
        if fp.tell() > 16777215:
            raise ValidationError("File is too large (16MB is the max file size)")
        fp.seek(0)

#---------------------------------------------------------------------------
# Extra fields and widgets
#---------------------------------------------------------------------------
from io import StringIO
from wtforms.fields  import SelectField
from wtforms.fields  import SelectMultipleField
from wtforms.fields  import Label
from wtforms.widgets import CheckboxInput
from wtforms.widgets import RadioInput
from wtforms.widgets import html_params, HTMLString
from datetime import datetime
from calendar import month_name


class RequiredLabel(Label):
    def __call__(self, text=None, **kwargs):
        kwargs['class_'] = kwargs.get('class_', "")+" is-required"
        return super(RequiredLabel, self).__call__(text, **kwargs)

class MonthField(SelectField):
    """
    Field to select a month
    """
    def __init__(self, label=None, validators=None, **kwargs):
        super(MonthField, self).__init__(label, validators, **kwargs)
        self.month = datetime.utcnow().month

    def iter_choices(self):
        months = [(month, name, month==self.month)
                  for month, name in enumerate(month_name)]
        return months

    def pre_validate(self, form):
        pass

class YearField(SelectField):
    """
    Field to select a year
    """
    def __init__(self, toYear=2014, label=None, validators=None, **kwargs):
        super(YearField, self).__init__(label, validators, **kwargs)
        self.year   = datetime.utcnow().year
        self.toYear = toYear

    def iter_choices(self):
        years = [(0, "", False), (self.year, str(self.year), True)]
        years.extend([(year, str(year), False)
                      for year in range(self.year - 1, self.toYear - 1, -1)])
        return years

    def pre_validate(self, form):
        pass

class MultiCheckboxWidget(object):
    def __init__(self):
        pass

    @staticmethod
    def javascript():
        retval = """\
<script type="text/javascript" charset="utf8">
     $(function () {
        $(".multi-checkboxes ul").selectable({
            'stop': function() {        
                $(".ui-selected input", this).each(function() {
                    this.checked = !this.checked;
                });
            }
        });
        $("a.tick-all").click(function() {
            var ourCbs = $(this).closest(".multi-checkboxes");
            ourCbs.find("ul li input", this).prop("checked", true);
        });
        $("a.tick-none").click(function() {
            var ourCbs = $(this).closest(".multi-checkboxes");
            ourCbs.find("ul li input").prop("checked", false);
        });
    });
</script>"""
        return retval

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs['class_'] = kwargs.get('class_', "")+" multi-checkboxes"
        body = StringIO()
        body.write('<div {}>'.format(html_params(**kwargs)))
        body.write('<div class="tick-checkboxes">')
        body.write('<b>tick:</b> ')
        body.write('<a href="javascript:void(0);" class="tick-all">all</a> ')
        body.write('<a href="javascript:void(0);" class="tick-none">none</a>')
        body.write('</div>')
        body.write('<ul>')
        for subfield in field:
            body.write(self.itemTag(subfield))
        body.write('</ul>')
        body.write('</div>')
        return HTMLString(body.getvalue())

    def itemTag(self, subfield):
        return '<li>{} {}</li>'.format(subfield(), subfield.label)

class MultiCheckboxField(SelectMultipleField):
    widget        = MultiCheckboxWidget()
    option_widget = CheckboxInput()

class MultiCountryWidget(MultiCheckboxWidget):
    def itemTag(self, subfield):
        code = subfield._value()
        flag = "famfamfam-flag-{}".format(code.lower())
        label = subfield.label('<i title="{}" class="{}"></i>{}'
                               .format(code, flag, subfield.label.text))
        return '<li>{} {}</li>'.format(subfield(), label)

class MultiCountryField(MultiCheckboxField):
    widget = MultiCountryWidget()

class SingleSelectionWidget(object):
    def __init__(self):
        pass

    @staticmethod
    def javascript():
        retval = """\
<script type="text/javascript" charset="utf8">
    $(function () {
        $(".single-selection .drop-down").selectable({
            'selecting': function (event, ui) {
                $(event.target).children('.ui-selecting').not(':first').removeClass('ui-selecting');
            },
            'selected': function(event, ui) {
                var radio = $(ui.selected).find("input[type=radio]");
                radio.prop("checked", true);
                onItemSelected(radio);
                $(this).hide();
            }
        });
        $(".single-selection .drop-down input[type=radio]").click(function() {
            onItemSelected($(this));
        });
        $(".single-selection .selection").click(function() {
            $(".single-selection .drop-down").toggle();
            return false;
        });
        $("#content").click(function() {
            $(".single-selection .drop-down").hide();
        });
    });
    function onItemSelected(item) {
        var ourSelection = item.closest(".single-selection").find(".selection");
        var ourLabel     = item.next("label");
        var newFlag      = ourLabel.find("i").clone();
        var newLabel     = $("<label>");
        newLabel.append(newFlag);
        newLabel.append( ourLabel.text());
        ourSelection.find("label").replaceWith(newLabel);
    }
</script>"""
        return retval

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs['class_'] = kwargs.get('class_', "")+" single-selection"
        body = StringIO()
        body.write('<div {}>'.format(html_params(**kwargs)))
        if field.coerce(field.data) == field.coerce(None):
            selected = next(iter(field))
        else:
            label = next((ch[1] for ch in field.choices 
                                if ch[0] == field.data), "")
            selected = field._Option(label=label, _name=field.name, _form=None)
            selected.process(None, field.data)
            selected.checked = True
        body.write(self.selection(selected))
        body.write(self.dropDown(field))
        body.write('</div>')
        return HTMLString(body.getvalue())

    def selection(self, field):
        retval = StringIO()
        retval.write('<div class="selection">')
        retval.write(field)
        retval.write('</div>')
        return HTMLString(retval.getvalue())

    def dropDown(self, field):
        retval = StringIO()
        retval.write('<div class="drop-holder">')
        retval.write('<ul class="drop-down">')
        for subfield in field:
            retval.write(self.itemTag(subfield))
        retval.write('</ul>')
        retval.write('</div>')
        return HTMLString(retval.getvalue())

    def itemTag(self, subfield):
        return '<li>{}</li>'.format(subfield.label.text)

class SingleSelectionField(SelectField):
    widget = SingleSelectionWidget()
    option_widget = RadioInput()

    def iter_choices(self):
        choiceIter = iter(self.choices)
        with suppress(StopIteration):
            value, label = next(choiceIter)
            if self.coerce(self.data) == self.coerce(None):
                yield (value, label, True)
            else:
                yield (value, label, self.coerce(value) == self.data)
        for value, label in choiceIter:
            if self.coerce(self.data) == self.coerce(None):
                selected = False
            else:
                selected = self.coerce(value) == self.data
            yield (value, label, selected)

class CountryWidget(SingleSelectionWidget):
    def selection(self, subfield):
        retval = StringIO()
        retval.write('<div class="selection">')
        code = subfield._value()
        flag = "famfamfam-flag-{}".format(code.lower())
        retval.write(subfield.label('<i title="{}" class="{}"></i>{}'
                                    .format(code, flag, subfield.label.text)))
        retval.write('<img class="expand-selection" width="21" height=21" '
                     'alt="+" src="/static/selection-expand-arrow.png" />')
        retval.write('</div>')
        return HTMLString(retval.getvalue())

    def itemTag(self, subfield):
        code = subfield._value()
        flag = "famfamfam-flag-{}".format(code.lower())
        label = subfield.label('<i title="{}" class="{}"></i>{}'
                               .format(code, flag, subfield.label.text))
        return '<li>{} {}</li>'.format(subfield, label)

class CountryField(SingleSelectionField):
    widget = CountryWidget()
