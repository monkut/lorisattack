from django.contrib import admin


class UserDatetimeModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):  # type: ignore

        if getattr(obj, 'created_datetime', None) is None:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):  # type: ignore
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if instance.created_datetime is None:
                instance.created_by = request.user  # only update created_by once!

            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()
