from django.contrib import admin
from django.apps import apps

Pain = apps.get_model('celebot', 'Pain')
Translate = apps.get_model('celebot', 'Translate')
Reaction = apps.get_model('celebot', 'Reaction')
Comment = apps.get_model('celebot', 'Comment')
ParentChildComment = apps.get_model('celebot', 'ParentChildComment')
Attachment = apps.get_model('celebot', 'Attachment')
Tag = apps.get_model('celebot', 'Tag')
TagItem = apps.get_model('celebot', 'TagItem')
TaggitTag = apps.get_model('taggit', 'Tag')


class TranslateInline(admin.StackedInline):
    model = Translate


class PainExtend(admin.ModelAdmin):
    model = Pain
    inlines = (TranslateInline,)


# Register your models here.
admin.site.register(Pain, PainExtend)
admin.site.register(Reaction)
admin.site.register(Comment)
admin.site.register(ParentChildComment)
admin.site.register(Attachment)


class TagItemList(admin.StackedInline):
    model = TagItem


class TagExtend(admin.ModelAdmin):
    model = Tag
    inlines = (TagItemList, )


admin.site.unregister(TaggitTag)
admin.site.register(Tag, TagExtend)
