$('#query-btn').click(function(){
    tb = $('table#bill-tbl');
    // remove table and input
    tb.find('tr.row[style!="display:none"]').remove();
    $('input#shop_comment-txt').val('');
    if (!$('#clear_shop-ckb').is(':checked')){
        $('#dropdown_shop-btn').text('选择取到衣物店铺');
    }
    ajax_bill_query = jQuery.ajax({
        url: '../../../laundry/bill_query',
        type: 'POST',
        data: {bid: $('#bid-txt').val()},
    });
    ajax_bill_query.always(function(){
        js_bill_ret = JSON.parse(ajax_bill_query.responseText);
        console.log(js_bill_ret);
        if ('errmsg' in js_bill_ret){
            bootbox.alert(js_bill_ret.errmsg);
            return;
        }
        name_map = {
            'bid':      '订单号',
            'get_time_0':   '取衣时间',
            'return_time_0':   '最晚送衣时间',
            'real_name':   '客户姓名',
            'phone':   '客户电话',
            //'status':   '订单状态',
            'address':  '客户地址',
            'comment':   '客户留言',
            'get_order':  '取衣受理单',
            'return_order':  '送衣受理单',
            'total':      '总价',
            'clothes':      '衣物信息',
        };
        status_map = {
            '0':        '准备',
            '5':        '未支付',
            '10':        '订单确认中',
            '20':        '物流确认中',
            '25':        '取衣中',
            '30':        '洗衣中',
            '40':        '送衣中',
            '50':        '待评价',
            '60':        '订单完成',
            '-10':        '用户取消',
            '-15':        '管理员取消',
            '-20':        '发生错误',
        };

        for (var name in name_map){
            tr = $('tr.row[style="display:none"]').clone();
            td_left = tr.find('td.col-md-4');
            td_right = tr.find('td.col-md-8');
            td_left.text( name_map[name] );
            td_right.text( js_bill_ret[name] );
            if ('comment' == name && '' === js_bill_ret[name])
                td_right.text('（空）');
            if ('status' == name){
                s_status = "（"+status_map[ js_bill_ret[name] ]+"）";
                td_right.text( td_right.text() + s_status );
            }
            if ('total' == name)
                td_right.text( '￥'+td_right.text());
            if ('clothes' == name){
                td_right.text('');
                clothes_dp = $('#clothes-dp[style="display:none"]').clone();
                clothes_ul = clothes_dp.find('ul');
                for (var clothe_idx in js_bill_ret[name]){
                    it_cloth = js_bill_ret[name][clothe_idx];
                    clothes_li = clothes_dp.find('li[style="display:none"]').clone();
                    clothes_li.text(it_cloth.name + ' ￥' + it_cloth.price +
                            '*' + it_cloth.number + '件 = ￥' + (it_cloth.price*it_cloth.number));
                    clothes_li.toggle();
                    clothes_ul.append(clothes_li);
                }
                td_right.append(clothes_dp);
                clothes_dp.toggle();
            }
            tr.toggle();
            tb.append(tr);
        }
        $('#shop_comment-txt').val(js_bill_ret.shop_comment || '');

    });
});
$(document).ready( function(){
});

$('div.dropdown ul').on('click', 'li a', function(){
    var s_sel = $(this).text();
    $(this).parents('.dropdown').find('#dropdown_shop-btn')
    .html(s_sel+' <span class="caret"></span>')
    .attr('name', $(this).attr('name'));
});

