from django.contrib import admin
from WCLaundry.models import QueryBill, SendBill

# Register your models here.
class QueryBillAdmin(admin.ModelAdmin):
    class Media:
        js = (
            '../media/js/jquery.min.js',
            '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js',
            '../media/js/bootbox.min.js',
        )
        css = {
            'all':(
                '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css',
                '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css',
            )
        }
    def has_add_permission(self, request):
        return False
    change_list_template = 'admin/WCLaundry/query_bill.html'

class SendBillAdmin(admin.ModelAdmin):
    class Media:
        js = (
            '../media/js/jquery.min.js',
            '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js',
            '../media/js/bootstrap-table.min.js',
            '../media/js/bootstrap-table-zh-CN.min.js',
            '../media/js/bootstrap-editable.min.js',
            '../media/js/bootbox.min.js',
            '../media/js/bootstrap-table-editable.js',
            '../media/js/bootstrap-paginator.js',
        )
        css = {
            'all':(
                '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css',
                '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css',
                '//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css',
                '../media/css/bootstrap-table.min.css',
                '../media/css/bootstrap-editable.css',
            )
        }
    def has_add_permission(self, request):
        return False
    change_list_template = 'admin/WCLaundry/send_bill.html'

admin.site.register(QueryBill, QueryBillAdmin)
admin.site.register(SendBill, SendBillAdmin)
