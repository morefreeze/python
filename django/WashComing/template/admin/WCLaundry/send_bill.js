function get_total_pages(method){
    ajax_get_total_pages = jQuery.ajax({
        url: '../../../laundry/get_total_pages',
        type: 'POST',
        data: {method: s_method,},
    });
    ajax_get_total_pages.always( function(){
        js_get_total_pages = JSON.parse(ajax_get_total_pages.responseText);
        if ('errmsg' in js_get_total_pages && js_get_total_pages.errmsg !== ''){
            bootbox.alert(js_get_total_pages.errmsg);
            return;
        }
        $('#paginator').bootstrapPaginator({
            'totalPages': js_get_total_pages.total,
        });
    });
}
function get_bills(method, page){
    if ('to_arrive' != method && 'to_send' != method && 'sent' != method)
        return;
    i_page = parseInt(page || 1);
    ajax_get_bills = jQuery.ajax({
        url: '../../../laundry/get_bills',
        type: 'POST',
        data: {method: method, page: i_page,},
    });
    ajax_get_bills.always( function(){
        js_get_bills = JSON.parse(ajax_get_bills.responseText);
        if (!'errno' in js_get_bills || js_get_bills.errno !== 0){
            bootbox.alert('发生了某些错误，请稍后重试');
            return;
        }
        $('#get_bills-tbl').bootstrapTable('load', js_get_bills.data);
        if ('to_arrive' == method){
            $('#get_bills-tbl').bootstrapTable('hideColumn', 'feedback');
        }
        else if ('to_send' == method){
            $('#get_bills-tbl').bootstrapTable('hideColumn', 'feedback');
        }
        else if( 'sent' == method){
            $('#get_bills-tbl').bootstrapTable('showColumn', 'feedback');
        }
    });
}
function make_clothes_btn(value, row, index){
    if (!js_get_bills.data[index].clothes)
        return '';
    clothes_dp = $('#clothes-dp[style="display:none"]').clone();
    clothes_ul = clothes_dp.find('ul');
    js_clothes = js_get_bills.data[index].clothes;
    for (var clothe_idx in js_clothes){
        it_cloth = js_clothes[clothe_idx];
        clothes_li = clothes_dp.find('li[style="display:none"]').clone();
        clothes_li.text(it_cloth.name + ' ￥' + it_cloth.price +
                '*' + it_cloth.number + '件 = ￥' + (it_cloth.price*it_cloth.number));
        clothes_li.toggle();
        clothes_ul.append(clothes_li);
    }
    return clothes_dp.html();
}
function make_confirm_btn(value, row, index){
    if ($('li#to_arrive-li').hasClass('active'))
        return '<button id="confirm_get_'+row.bid+'-btn"class="btn btn-success btn-success-lg" name="'+row.bid+'">确认收衣</button>';
    if ($('li#to_send-li').hasClass('active'))
        return '<button id="confirm_return_'+row.bid+'-btn"class="btn btn-success btn-success-lg" name="'+row.bid+'">确认送回</button>';
    if ($('li#sent-li').hasClass('active'))
        return '';
        //return '<button id="confirm_'+row.bid+'-btn"class="btn btn-success btn-success-lg" name="'+row.bid+'">修改备注</button>';
}

$('ul.nav.nav-pills li').click( function(){
    s_method = $(this).attr('id');
    s_method = s_method.substring(s_method, s_method.length-3);
    $('ul.nav.nav-pills li').removeClass('active');
    $(this).addClass('active');
    get_bills(s_method);
    get_total_pages(s_method);
    if ($('#paginator').bootstrapPaginator('getPages').length > 0){
        $('#paginator').bootstrapPaginator('showFirst');
    }
});
$(document).ready( function(){
    get_bills('to_arrive');
    $('#get_bills-tbl').bootstrapTable({
        search: true,
        cache: true,
        columns: [
        {
            field: 'bid',
            title: '订单号',
            sortable: true,
            searchable: true,
        },
        {
            field: 'shop_name',
            title: '收到店铺',
            sortable: true,
            searchable: false,
        },
        {
            field: 'get_time_0',
            title: '取衣时间',
            sortable: true,
            searchable: false,
        },
        {
            field: 'return_time_0',
            title: '最晚送衣时间',
            sortable: true,
            searchable: false,
        },
        {
            field: 'real_name',
            title: '客户姓名',
            searchable: true,
        },
        {
            field: 'phone',
            title: '客户电话',
            searchable: true,
        },
        {
            field: 'address',
            title: '客户地址',
            searchable: false,
        },
        {
            field: 'shop_comment',
            title: '店铺备注',
            editable: {
                type: 'textarea',
            },
            searchable: false,
        },
        {
            field: 'feedback',
            title: '客户评价',
            searchable: false,
        },
        {
            field: 'total',
            title: '总价',
            sortable: true,
            formatter: function(value, row, index){ return '￥'+value; },
            searchable: false,
        },
        {
            field: 'clothes',
            title: '衣物详情',
            searchable: false,
            formatter: make_clothes_btn,
        },
        {
            field: 'operate',
            title: '操作',
            searchable: false,
            formatter: make_confirm_btn,
        },
        ],
    });

    $('#paginator').bootstrapPaginator({
        'onPageChanged': function(event, i_old_page, i_new_page){
            get_bills(s_method, i_new_page);
        },
    });
    s_method = $('ul.nav.nav-pills li.active').attr('id');
    s_method = s_method.substring(s_method, s_method.length-3);
    get_total_pages(s_method);
});

// confirm get button
$(s_method = 'table#get_bills-tbl').on('click', 'button[id^=confirm_get]', function(){
    s_bid = $(this).attr('name');
    s_shop_comment = $(this).parents('tr').find('[data-name=shop_comment]').text() || '';
    ajax_confirm_get = jQuery.ajax({
        url: '../../../laundry/confirm_get',
        type: 'POST',
        data: {bid: s_bid, shop_comment: s_shop_comment,},
    });
    ajax_confirm_get.always( function(){
        js_confirm_get = JSON.parse(ajax_confirm_get.responseText);
        if ('errmsg' in js_confirm_get && js_confirm_get.errmsg !== ''){
            bootbox.alert(js_confirm_get.errmsg);
            return;
        }
        bootbox.alert('确认收衣成功！请在待发回订单中查看。');
        s_method = $('ul.nav.nav-pills li.active').attr('id');
        s_method = s_method.substring(s_method, s_method.length-3);
        get_bills(s_method);
        get_total_pages(s_method);
    });
});
// confirm return button
$(s_method = 'table#get_bills-tbl').on('click', 'button[id^=confirm_return]', function(){
    s_bid = $(this).attr('name');
    s_shop_comment = $(this).parents('tr').find('[data-name=shop_comment]').text() || '';
    ajax_confirm_return = jQuery.ajax({
        url: '../../../laundry/confirm_return',
        type: 'POST',
        data: {bid: s_bid, shop_comment: s_shop_comment,},
    });
    ajax_confirm_return.always( function(){
        js_confirm_return = JSON.parse(ajax_confirm_return.responseText);
        if ('errmsg' in js_confirm_return && js_confirm_return.errmsg !== ''){
            bootbox.alert(js_confirm_return.errmsg);
            return;
        }
        bootbox.alert('确认送回成功！请稍后在已发订单中查看送回受理单号。');
        s_method = $('ul.nav.nav-pills li.active').attr('id');
        s_method = s_method.substring(s_method, s_method.length-3);
        get_bills(s_method);
        get_total_pages(s_method);
    });
});

