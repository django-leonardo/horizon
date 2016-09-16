import six
from django import forms, template
from django.forms.forms import NON_FIELD_ERRORS  # noqa
from django.template.defaultfilters import linebreaks  # noqa
from django.template.defaultfilters import safe  # noqa
from django.template.defaultfilters import slugify
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from horizon import workflows


class ModelFormOptions(forms.models.ModelFormOptions):

    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.fields = getattr(options, 'fields', None)
        self.exclude = getattr(options, 'exclude', None)
        self.widgets = getattr(options, 'widgets', None)
        self.localized_fields = getattr(options, 'localized_fields', None)
        self.labels = getattr(options, 'labels', None)
        self.help_texts = getattr(options, 'help_texts', None)
        self.error_messages = getattr(options, 'error_messages', None)
        self.field_classes = getattr(options, 'field_classes', None)


class ActionMetaclass(forms.models.ModelFormMetaclass):

    def __new__(mcs, name, bases, attrs):
        # Pop Meta for later processing
        opts = attrs.pop("Meta", None)
        # Create our new class
        cls = super(ActionMetaclass, mcs).__new__(mcs, name, bases, attrs)
        # Process options from Meta
        cls.name = getattr(opts, "name", name)
        cls.slug = getattr(opts, "slug", slugify(name))
        cls.permissions = getattr(opts, "permissions", ())
        cls.progress_message = getattr(opts,
                                       "progress_message",
                                       _("Processing..."))
        cls.help_text = getattr(opts, "help_text", "")
        cls.context_name = getattr(opts, "context_name", None)

        cls.help_text_template = getattr(opts, "help_text_template", None)
        opts = cls._meta = ModelFormOptions(opts)

        if cls._meta.model:

            fields = forms.models.fields_for_model(
                opts.model, opts.fields, opts.exclude,
                opts.widgets, None,
                opts.localized_fields, opts.labels,
                opts.help_texts, opts.error_messages)

            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(cls.declared_fields)
        else:
            fields = cls.declared_fields

        cls.base_fields = fields

        return cls


@six.python_2_unicode_compatible
class ModelAction(six.with_metaclass(ActionMetaclass,
                                     forms.ModelForm)):

    """Model action which is based on

    model form with same API like horizon.Action has
    """

    def __init__(self, request, context, instance=None,
                 prefix=None, *args, **kwargs):

        context_model_name = self.context_name or self._meta.model._meta.model_name.lower()

        if context_model_name in context:
            instance = context[context_model_name]

        if request.method == "POST":
            super(ModelAction, self).__init__(request.POST,
                                              initial=context,
                                              instance=instance,
                                              prefix=prefix)
        else:
            super(ModelAction, self).__init__(
                initial=context, instance=instance,
                prefix=prefix)

        if not hasattr(self, "handle"):
            raise AttributeError("The action %s must define a handle method."
                                 % self.__class__.__name__)

        self.request = request
        self._populate_choices(request, context)
        self.required_css_class = 'required'

    def __str__(self):
        return force_text(self.name)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.slug)

    def _populate_choices(self, request, context):
        for field_name, bound_field in self.fields.items():
            meth = getattr(self, "populate_%s_choices" % field_name, None)
            if meth is not None and callable(meth):
                bound_field.choices = meth(request, context)

    def get_help_text(self, extra_context=None):
        """Returns the help text for this step."""
        text = ""
        extra_context = extra_context or {}
        if self.help_text_template:
            tmpl = template.loader.get_template(self.help_text_template)
            context = template.RequestContext(self.request, extra_context)
            text += tmpl.render(context)
        else:
            text += linebreaks(force_text(self.help_text))
        return safe(text)

    def add_action_error(self, message):
        """Adds an error to the Action's Step based on API issues."""
        self.errors[NON_FIELD_ERRORS] = self.error_class([message])

    @sensitive_variables('context')
    def handle(self, request, context):
        """Handles any requisite processing for this action. The method should
        return either ``None`` or a dictionary of data to be passed to
        :meth:`~horizon.workflows.Step.contribute`.
        Returns ``None`` by default, effectively making it a no-op.
        """

        self.save()


class ModelStep(workflows.Step):

    """Base Step for models

    decalare prefix = my_model_name
    and fields like a contributes
    then provide my_model_name to context_seed
    if you have instance

    on your ModelAction use same prefix
    and in handle method use self.cleaned_data
    instead context parameter !
    """

    @property
    def contributes(self):

        prefix_contributes = [self.prefix]
        for contribute in self.fields:
            prefix_contributes.append(self.add_prefix(contribute))
        return prefix_contributes

    def add_prefix(self, field_name):
        """
        Returns the field name with a prefix appended, if this Form has a
        prefix set.
        Subclasses may wish to override.
        """
        return '%s-%s' % (self.prefix, field_name) if self.prefix else field_name
