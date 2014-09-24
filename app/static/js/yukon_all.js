/* Yukon Admin all functions
 *
 * Content:
 *
 * 1. Helpers
 * 2. Common functions
 * 3. Plugins
 *   3.1
 *   3.2
 *
 *
 * */


    $(function () {

        /* bootstrap custom functions */
        yukon_bs_custom.accordion_active_class();
        yukon_bs_custom.dropdown_click();
        yukon_bs_custom.tooltips_init();
        yukon_bs_custom.popover_init();

        /* side menu */
        yukon_side_menu.init();

        /* style switcher */
        yukon_style_switcher.init();

    });


/* Helpers */
    /* Detect touch devices */
    function is_touch_device() {
        return !!('ontouchstart' in window);
    }
    /* Detect hi-res devices */
    function isHighDensity() {
        return ((window.matchMedia && (window.matchMedia('only screen and (min-resolution: 124dpi), only screen and (min-resolution: 1.3dppx), only screen and (min-resolution: 48.8dpcm)').matches || window.matchMedia('only screen and (-webkit-min-device-pixel-ratio: 1.3), only screen and (-o-min-device-pixel-ratio: 2.6/2), only screen and (min--moz-device-pixel-ratio: 1.3), only screen and (min-device-pixel-ratio: 1.3)').matches)) || (window.devicePixelRatio && window.devicePixelRatio > 1.3));
    }
	/*
	* debouncedresize: special jQuery event that happens once after a window resize
	* throttledresize: special jQuery event that happens at a reduced rate compared to "resize"
	*
	* latest version and complete README available on Github:
	* https://github.com/louisremi/jquery-smartresize
	*
	* Copyright 2012 @louis_remi
	* Licensed under the MIT license.
    *
	*/
	(function(a){var d=a.event,b,c;b=d.special.debouncedresize={setup:function(){a(this).on("resize",b.handler)},teardown:function(){a(this).off("resize",b.handler)},handler:function(a,f){var g=this,h=arguments,e=function(){a.type="debouncedresize";d.dispatch.apply(g,h)};c&&clearTimeout(c);f?e():c=setTimeout(e,b.threshold)},threshold:150}})(jQuery);
    (function(b){var f=b.event,c,g={_:0},a=0,d,e;c=f.special.throttledresize={setup:function(){b(this).on("resize",c.handler)},teardown:function(){b(this).off("resize",c.handler)},handler:function(h,k){var l=this,m=arguments;d=!0;e||(setInterval(function(){a++;if(a>c.threshold&&d||k)h.type="throttledresize",f.dispatch.apply(l,m),d=!1,a=0;9<a&&(b(g).stop(),e=!1,a=0)},30),e=!0)},threshold:0}})(jQuery);

/* common functions */

    /* side menu */
    yukon_side_menu = {
        init: function () {

            // add '.has_submenu' class if section has childrens
            $('#main_menu ul > li').each(function () {
                if ($(this).children('ul').length) {
                    $(this).addClass('has_submenu');
                }
            });

            // side menu accordion
            $('.side_menu_expanded #main_menu').on('click', '.has_submenu > a', function () {
                var $this_parent = $(this).parent('.has_submenu'),
                    panel_active = $this_parent.hasClass('section_active');
                $this_parent.siblings().removeClass('section_active').children('ul').slideUp('200');
                if (!panel_active) {
                    $this_parent.addClass('section_active').children('ul').slideDown('200');
                } else {
                    $this_parent.removeClass('section_active').children('ul').slideUp('200');
                }
            });

            // side menu initialization
            $('#main_menu .has_submenu .act_nav').parents('.has_submenu').children('a').click();

            $('.menu_toggle').click(function() {
                if($('body').hasClass('side_menu_expanded')) {
                    yukon_side_menu.menu_collapse();
                } else if($('body').hasClass('side_menu_collapsed')) {
                    yukon_side_menu.menu_expand();
                }
                $(window).trigger('resize');
            });

            // update side navigation position on window resize/orientation change
            $(window).on("debouncedresize", function( event ) {
                if($('body').hasClass('side_menu_expanded') && $(window).width() <= 992 ) {
                    yukon_side_menu.menu_collapse();
                }
            });

            // collapse navigation on mobile devices
            if($('body').hasClass('side_menu_expanded') && $(window).width() <= 992 ) {
                yukon_side_menu.menu_collapse();
            }

            // uncomment function bellow to activate saving side menu states
            //yukon_side_menu.menu_cookie();

        },
        menu_expand: function() {
            $('body').addClass('side_menu_expanded').removeClass('side_menu_collapsed');
            $('.menu_toggle').find('.toggle_left').show();
            $('.menu_toggle').find('.toggle_right').hide();
        },
        menu_collapse: function() {
            $('body').removeClass('side_menu_expanded').addClass('side_menu_collapsed');
            $('.menu_toggle').find('.toggle_left').hide();
            $('.menu_toggle').find('.toggle_right').show();
        },
        menu_cookie: function() {
            $('.menu_toggle').on('click',function() {
                if($('body').hasClass('side_menu_expanded')) {
                    $.cookie('side_menu', '1');
                } else if($('body').hasClass('side_menu_collapsed')) {
                    $.cookie('side_menu', '0');
                }
            });

            var $side_menu_cookie = $.cookie('side_menu');

            if($side_menu_cookie != undefined) {
                if($side_menu_cookie == '1') {
                    yukon_side_menu.menu_expand();
                } else if($side_menu_cookie == '0') {
                    yukon_side_menu.menu_collapse();
                }
            }
        }
    };

    // style switcher
    yukon_style_switcher = {
        init: function() {
            var $styleSwitcher = $('#style_switcher');

            // toggle style switcher
            $('.switcher_toggle').on('click', function(e) {
                if(!$styleSwitcher.hasClass('switcher_open')) {
                    $styleSwitcher.addClass('switcher_open')
                } else {
                    $styleSwitcher.removeClass('switcher_open')
                }
                e.preventDefault();
            })

            // layout
            $('#layout_style_switch').val('').on('change', function() {
                $this_val = $(this).val();
                if($this_val == 'fixed') {
                    $('body').addClass('fixed_layout');
                }
                if($this_val == 'full_width') {
                    $('body').removeClass('fixed_layout');
                }
                $(window).resize();
            })

			// top bar style
            $('#topBar_style_switch li').on('click',function() {
                var topBarStyle = $(this).attr('title');
                $('#topBar_style_switch li').removeClass('style_active');
                $(this).addClass('style_active');
                $('#main_header').removeClass('topBar_style_1 topBar_style_2 topBar_style_3 topBar_style_4 topBar_style_5 topBar_style_6 topBar_style_7 topBar_style_8 topBar_style_9 topBar_style_10 topBar_style_11 topBar_style_12 topBar_style_13 topBar_style_14').addClass(topBarStyle);
            });
        }
    }

    // bootstrap custom functions
    yukon_bs_custom = {
        accordion_active_class: function() {
            if($('.panel-collapse').length) {
                $('.panel-collapse.in').closest('.panel').addClass('panel-active');
                $('.panel-collapse').on('hide.bs.collapse', function () {
                    $(this).closest('.panel').removeClass('panel-active');
                }).on('show.bs.collapse', function () {
                    $(this).closest('.panel').addClass('panel-active');
                })
            }
        },
        dropdown_click: function() {
            // prevent closing notification dropdown on content click
            if($('.header_notifications .dropdown-menu').length) {
                $('.header_notifications .dropdown-menu').click(function(e) {
                    e.stopPropagation();
                });
            }
        },
        tooltips_init: function() {
            $('.bs_ttip').tooltip({
                container: 'body'
            });
        },
        popover_init: function() {
            $('.bs_popup').popover({
                container: 'body'
            });
        }
    };

/* page specific functions */
    // chat
    yukon_chat = {
        init: function() {
            if($('.chat_message_send button').length) {
                var msg_date_unix;
                $('.chat_message_send button').on('click', function() {
                    var msg_date = moment().format('MMM D YYYY, h:mm A'),
                        chat_msg = $('.chat_message_send textarea').val();
                    if(chat_msg != '') {
                        if( msg_date != $('.chat_messages').data('lastMessageUnix') ) {
                            $('.chat_messages').prepend('<div class="message_date">'+ msg_date +'</div><ul></ul>').data('lastMessageUnix', msg_date);
                        }
                        $('.chat_messages ul:first').prepend('<li class="msg_left"><p class="msg_user">Carrol Clark</p>' + chat_msg + '</li>');
                        $('.chat_message_send textarea').val('');
                    }
                })
            }
        }
    };

    // mailbox
    yukon_mailbox = {
        init: function() {
            var $mailbox_table = $('#mailbox_table');

            $mailbox_table.find('.mbox_star span').on('click', function(){
                var $this = $(this),
                    $this_parent = $this.parent('.mbox_star');

                $this.hasClass('icon_star') ? $this_parent.removeClass('marked') : $this_parent.addClass('marked');

                $this.toggleClass('icon_star icon_star_alt');

            });

            $('input.msgSelect').on('click',function() {
                $(this).is(':checked') ? $(this).closest('tr').addClass('selected') : $(this).closest('tr').removeClass('selected');
            });

            $mailbox_table.on('click', '#msgSelectAll', function () {
                var $this = $(this);

                $mailbox_table.find('input.msgSelect').filter(':visible').each(function() {
                    $this.is(':checked') ? $(this).prop('checked',true).closest('tr').addClass('selected') : $(this).prop('checked',false).closest('tr').removeClass('selected');
                })

            })
        }
    };

    // user list
    yukon_user_list = {
        init: function() {
            $('.countUsers').text($('#user_list > li').length);
        }
    };

    // icons
    yukon_icons = {
        search_icons: function() {
            $('#icon_search').val('').keyup(function(){

                var sValue = $(this).val().toLowerCase();
                $('.icon_list > li > span').each(function () {
                    if ($(this).attr('class').toLowerCase().indexOf(sValue) === -1) {
                        $(this).parent('li').hide();
                    } else {
                        $(this).parent('li').show();
                    }
                });

            });
        }
    };

    // gallery
    yukon_gallery = {
        search_gallery: function() {
            $('#gallery_search').val('').keyup(function(){

                var sValue = $(this).val().toLowerCase();

                $('.gallery_grid > li > a').each(function () {
                    if( $(this).text().search(new RegExp(sValue, "i")) < 0 && $(this).attr('title').toLowerCase().indexOf(sValue) === -1 ) {
                        $(this).closest('li').hide();
                    } else {
                        $(this).closest('li').show();
                    }
                });

            });
        }
    };

/* plugins */

    // full calendar
    yukon_fullCalendar = {
        p_plugins_calendar: function() {
            if($('#calendar').length) {
                var date = new Date();
                var d = date.getDate();
                var m = date.getMonth();
                var y = date.getFullYear();

                $('#calendar').fullCalendar({
                    header: {
                        center: 'title',
                        left: 'month,agendaWeek,agendaDay today',
                        right: 'prev,next'
                    },
                    buttonIcons: {
                        prev: ' el-icon-chevron-left',
                        next: ' el-icon-chevron-right'
                    },
                    editable: true,
                    aspectRatio: 2.2,
                    events: [
                        {
                            title: 'All Day Event',
                            start: new Date(y, m, 1)
                        },
                        {
                            title: 'Long Event',
                            start: new Date(y, m, d - 5),
                            end: new Date(y, m, d - 2)
                        },
                        {
                            id: 999,
                            title: 'Repeating Event',
                            start: new Date(y, m, d - 3, 16, 0)
                        },
                        {
                            id: 999,
                            title: 'Repeating Event',
                            start: new Date(y, m, d + 4, 16, 0)
                        },
                        {
                            title: 'Meeting',
                            start:  new Date(y, m, d + 1, 19, 0),
                            end:  new Date(y, m, d + 1, 22, 30)
                        },
                        {
                            title: 'Lunch',
                            start: new Date(y, m, d - 7)
                        },
                        {
                            title: 'Birthday Party',
                            start: new Date(y, m, d + 10)
                        },
                        {
                            title: 'Click for Google',
                            url: 'http://google.com/',
                            start: new Date(y, m, d + 12)
                        }
                    ],
                    eventAfterAllRender: function() {
                        $('.fc-header .fc-button-prev').html('<span class="el-icon-chevron-left"></span>');
                        $('.fc-header .fc-button-next').html('<span class="el-icon-chevron-right"></span>');
                    }
                });
            }

            if($('#calendar_phases').length) {
                $('#calendar_phases').fullCalendar({
                    header: {
                        center: 'title',
                        left: 'month,agendaWeek,agendaDay today',
                        right: 'prev,next'
                    },
                    buttonIcons: false,
                    aspectRatio: 2.2,
                    // Phases of the Moon
                    events: 'https://www.google.com/calendar/feeds/ht3jlfaac5lfd6263ulfh4tql8%40group.calendar.google.com/public/basic',
                    eventClick: function(event) {
                        // opens events in a popup window
                        window.open(event.url, 'gcalevent', 'width=700,height=600');
                        return false;
                    },
                    eventAfterAllRender: function() {
                        $('.fc-header .fc-button-prev').html('<span class="el-icon-chevron-left"></span>');
                        $('.fc-header .fc-button-next').html('<span class="el-icon-chevron-right"></span>');
                    }
                });
            }
        }
    };

    // c3 charts
    yukon_charts = {
        p_dashboard: function() {
            if($('#c3_7_days').length) {
                var c3_7_days_chart = c3.generate({
                    bindto: '#c3_7_days',
                    data: {
                        x: 'x',
                        columns: [
                            ['x', '2013-01-01', '2013-02-01', '2013-03-01', '2013-04-01', '2013-05-01', '2013-06-01', '2013-07-01', '2013-08-01', '2013-09-01', '2013-10-01', '2013-11-01', '2013-12-01'],
                            ['2013', 14512, 10736, 18342, 14582, 16304, 22799, 18833, 21973, 23643, 22488, 24752, 28722],
                            ['2014', 23732, 22904, 23643, 26887, 32629, 30512, 31658, 35782, 36724, 38947, 42426, 37439]
                        ],
                        types: {
                            '2013': 'area',
                            '2014': 'line'
                        }
                    },
                    axis: {
                        x: {
                            type: 'timeseries',
                            tick: {
                                culling: false,
                                fit: true,
                                format: "%b"
                            }
                        },
                        y : {
                            tick: {
                                format: d3.format("$,")
                            }
                        }
                    },
                    point: {
                        r: '4',
                        focus: {
                            expand: {
                                r: '5'
                            }
                        }
                    },
                    bar: {
                        width: {
                            ratio: 0.4 // this makes bar width 50% of length between ticks
                        }
                    },
                    grid: {
                        x: {
                            show: true
                        },
                        y: {
                            show: true
                        }
                    },
                    color: {
                        pattern: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                    }
                });

                $('.chart_switch').on('click', function() {

                    if($(this).data('chart') == 'line') {
                        c3_7_days_chart.transform('area', '2013');
                        c3_7_days_chart.transform('line', '2014');
                    } else if($(this).data('chart') == 'bar') {
                        c3_7_days_chart.transform('bar');
                    }

                    $('.chart_switch').toggleClass('btn-default btn-link');

                });

                $(window).on("debouncedresize", function() {
                    c3_7_days_chart.resize();
                });
            }
            if($('#c3_orders').length) {
                var c3_orders_chart = c3.generate({
                    bindto: '#c3_orders',
                    data: {
                        columns: [
                            ['New', 64],
                            ['In Progrees', 36]

                        ],
                        type : 'pie'
                    },
                    pie: {
                        //onclick: function (d, i) { console.log(d, i); },
                        //onmouseover: function (d, i) { console.log(d, i); },
                        //onmouseout: function (d, i) { console.log(d, i); }
                    }
                });
                $(window).on("debouncedresize", function() {
                    c3_orders_chart.resize();
                });
            }
            if($('#c3_users_age').length) {
                var c3_users_age = c3.generate({
                    bindto: '#c3_users_age',
                    data: {
                        columns: [
                            ['18-24', 18],
                            ['25-32', 42],
                            ['33-40', 31],
                            ['41-57', 9]

                        ],
                        type : 'donut'
                    },
                    donut: {
                        //onclick: function (d, i) { console.log(d, i); },
                        //onmouseover: function (d, i) { console.log(d, i); },
                        //onmouseout: function (d, i) { console.log(d, i); }
                    }
                });
                $(window).on("debouncedresize", function() {
                    c3_users_age.resize();
                });
            }
        },
        p_plugins_charts: function() {

            // combined chart
            var c3_combined_chart = c3.generate({
                bindto: '#c3_combined',
                data: {
                    columns: [
                        ['data1', 30, 20, 50, 40, 60, 50],
                        ['data2', 200, 130, 90, 240, 130, 220],
                        ['data3', 200, 130, 90, 240, 130, 220],
                        ['data4', 130, 120, 150, 140, 160, 150],
                        ['data5', 90, 70, 20, 50, 60, 120]
                    ],
                    type: 'bar',
                    types: {
                        data3: 'line',
                        data5: 'area'
                    },
                    groups: [
                        ['data1','data2']
                    ]
                },
                point: {
                    r: '4',
                    focus: {
                        expand: {
                            r: '5'
                        }
                    }
                },
                bar: {
                    width: {
                        ratio: 0.4 // this makes bar width 50% of length between ticks
                    }
                },
                grid: {
                    x: {
                        show: true
                    },
                    y: {
                        show: true
                    }
                },
                color: {
					pattern: ['#ff7f0e', '#2ca02c', '#9467bd', '#1f77b4', '#d62728']
				}
            });

            // gauge chart
            var chart_gauge = c3.generate({
                bindto: '#c3_gauge',
                data: {
                    columns: [
                        ['data', 91.4]
                    ],
                    type: 'gauge'
                    //onclick: function (d, i) { console.log("onclick", d, i); },
                    //onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                    //onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                },
                gauge: {
                    width: 39
                },
                color: {
                    pattern: ['#ff0000', '#f97600', '#f6c600', '#60b044'],
                    threshold: {
                        values: [30, 60, 90, 100]
                    }
                }
            });

            setTimeout(function () {
                chart_gauge.load({
                    columns: [['data', 10]]
                });
            }, 2000);
            setTimeout(function () {
                chart_gauge.load({
                    columns: [['data', 50]]
                });
            }, 3000);
            setTimeout(function () {
                chart_gauge.load({
                    columns: [['data', 70]]
                });
            }, 4000);
            setTimeout(function () {
                chart_gauge.load({
                    columns: [['data', 0]]
                });
            }, 5000);
            setTimeout(function () {
                chart_gauge.load({
                    columns: [['data', 100]]
                });
            }, 6000);

            // donut chart
            var chart_donut = c3.generate({
                bindto: '#c3_donut',
                data: {
                    columns: [
                        ['data1', 30],
                        ['data2', 120]
                    ],
                    type : 'donut',
                    onclick: function (d, i) { console.log("onclick", d, i); },
                    onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                    onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                },
                donut: {
                    title: "Iris Petal Width"
                }
            });
            setTimeout(function () {
                chart_donut.load({
                    columns: [
                        ["setosa", 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3, 0.2, 0.4, 0.2, 0.5, 0.2, 0.2, 0.4, 0.2, 0.2, 0.2, 0.2, 0.4, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.2, 0.2, 0.3, 0.3, 0.2, 0.6, 0.4, 0.3, 0.2, 0.2, 0.2, 0.2],
                        ["versicolor", 1.4, 1.5, 1.5, 1.3, 1.5, 1.3, 1.6, 1.0, 1.3, 1.4, 1.0, 1.5, 1.0, 1.4, 1.3, 1.4, 1.5, 1.0, 1.5, 1.1, 1.8, 1.3, 1.5, 1.2, 1.3, 1.4, 1.4, 1.7, 1.5, 1.0, 1.1, 1.0, 1.2, 1.6, 1.5, 1.6, 1.5, 1.3, 1.3, 1.3, 1.2, 1.4, 1.2, 1.0, 1.3, 1.2, 1.3, 1.3, 1.1, 1.3],
                        ["virginica", 2.5, 1.9, 2.1, 1.8, 2.2, 2.1, 1.7, 1.8, 1.8, 2.5, 2.0, 1.9, 2.1, 2.0, 2.4, 2.3, 1.8, 2.2, 2.3, 1.5, 2.3, 2.0, 2.0, 1.8, 2.1, 1.8, 1.8, 1.8, 2.1, 1.6, 1.9, 2.0, 2.2, 1.5, 1.4, 2.3, 2.4, 1.8, 1.8, 2.1, 2.4, 2.3, 1.9, 2.3, 2.5, 2.3, 1.9, 2.0, 2.3, 1.8]
                    ]
                });
            }, 2500);
            setTimeout(function () {
                chart_donut.unload({
                    ids: 'data1'
                });
                chart_donut.unload({
                    ids: 'data2'
                });
            }, 4500);

            // grid lines
            var chart_grid_lines = c3.generate({
                bindto: '#c3_grid_lines',
                data: {
                    columns: [
                        ['sample', 30, 200, 100, 400, 150, 250],
                        ['sample2', 1300, 1200, 1100, 1400, 1500, 1250]
                    ],
                    axes: {
                        sample2: 'y2'
                    }
                },
                axis: {
                    y2: {
                        show: true
                    }
                },
                grid: {
                    y: {
                        lines: [{value: 50, text: 'Label 50'}, {value: 1300, text: 'Label 1300', axis: 'y2'}]
                    }
                }
            });

            // scatter plot
            var chart_scatter = c3.generate({
                bindto: '#c3_scatter',
                data: {
                    xs: {
                        setosa: 'setosa_x',
                        versicolor: 'versicolor_x'
                    },
                    // iris data from R
                    columns: [
                        ["setosa_x", 3.5, 3.0, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1, 3.7, 3.4, 3.0, 3.0, 4.0, 4.4, 3.9, 3.5, 3.8, 3.8, 3.4, 3.7, 3.6, 3.3, 3.4, 3.0, 3.4, 3.5, 3.4, 3.2, 3.1, 3.4, 4.1, 4.2, 3.1, 3.2, 3.5, 3.6, 3.0, 3.4, 3.5, 2.3, 3.2, 3.5, 3.8, 3.0, 3.8, 3.2, 3.7, 3.3],
                        ["versicolor_x", 3.2, 3.2, 3.1, 2.3, 2.8, 2.8, 3.3, 2.4, 2.9, 2.7, 2.0, 3.0, 2.2, 2.9, 2.9, 3.1, 3.0, 2.7, 2.2, 2.5, 3.2, 2.8, 2.5, 2.8, 2.9, 3.0, 2.8, 3.0, 2.9, 2.6, 2.4, 2.4, 2.7, 2.7, 3.0, 3.4, 3.1, 2.3, 3.0, 2.5, 2.6, 3.0, 2.6, 2.3, 2.7, 3.0, 2.9, 2.9, 2.5, 2.8],
                        ["setosa", 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3, 0.2, 0.4, 0.2, 0.5, 0.2, 0.2, 0.4, 0.2, 0.2, 0.2, 0.2, 0.4, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.2, 0.2, 0.3, 0.3, 0.2, 0.6, 0.4, 0.3, 0.2, 0.2, 0.2, 0.2],
                        ["versicolor", 1.4, 1.5, 1.5, 1.3, 1.5, 1.3, 1.6, 1.0, 1.3, 1.4, 1.0, 1.5, 1.0, 1.4, 1.3, 1.4, 1.5, 1.0, 1.5, 1.1, 1.8, 1.3, 1.5, 1.2, 1.3, 1.4, 1.4, 1.7, 1.5, 1.0, 1.1, 1.0, 1.2, 1.6, 1.5, 1.6, 1.5, 1.3, 1.3, 1.3, 1.2, 1.4, 1.2, 1.0, 1.3, 1.2, 1.3, 1.3, 1.1, 1.3]
                    ],
                    type: 'scatter'
                },
                axis: {
                    x: {
                        label: 'Sepal.Width',
                        tick: {
                            fit: false
                        }
                    },
                    y: {
                        label: 'Petal.Width'
                    }
                }
            });

            setTimeout(function () {
                chart_scatter.load({
                    xs: {
                        virginica: 'virginica_x'
                    },
                    columns: [
                        ["virginica_x", 3.3, 2.7, 3.0, 2.9, 3.0, 3.0, 2.5, 2.9, 2.5, 3.6, 3.2, 2.7, 3.0, 2.5, 2.8, 3.2, 3.0, 3.8, 2.6, 2.2, 3.2, 2.8, 2.8, 2.7, 3.3, 3.2, 2.8, 3.0, 2.8, 3.0, 2.8, 3.8, 2.8, 2.8, 2.6, 3.0, 3.4, 3.1, 3.0, 3.1, 3.1, 3.1, 2.7, 3.2, 3.3, 3.0, 2.5, 3.0, 3.4, 3.0],
                        ["virginica", 2.5, 1.9, 2.1, 1.8, 2.2, 2.1, 1.7, 1.8, 1.8, 2.5, 2.0, 1.9, 2.1, 2.0, 2.4, 2.3, 1.8, 2.2, 2.3, 1.5, 2.3, 2.0, 2.0, 1.8, 2.1, 1.8, 1.8, 1.8, 2.1, 1.6, 1.9, 2.0, 2.2, 1.5, 1.4, 2.3, 2.4, 1.8, 1.8, 2.1, 2.4, 2.3, 1.9, 2.3, 2.5, 2.3, 1.9, 2.0, 2.3, 1.8]
                    ]
                });
            }, 1000);

            setTimeout(function () {
                chart_scatter.unload({
                    ids: 'setosa'
                });
            }, 2000);

            setTimeout(function () {
                chart_scatter.load({
                    columns: [
                        ["virginica", 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3, 0.2, 0.4, 0.2, 0.5, 0.2, 0.2, 0.4, 0.2, 0.2, 0.2, 0.2, 0.4, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.2, 0.2, 0.3, 0.3, 0.2, 0.6, 0.4, 0.3, 0.2, 0.2, 0.2, 0.2]
                    ]
                });
            }, 3000);

            // resize charts
            $(window).on("debouncedresize", function() {
                c3_combined_chart.resize();
                chart_gauge.resize();
                chart_donut.resize();
                chart_grid_lines.resize();
                chart_scatter.resize();
            });
        }
    };

    // countUp animation
    yukon_count_up = {
        init: function() {
            if($('.countUpMe').length) {
                $('.countUpMe').each(function() {
                    var target = this;
                    var endVal = parseInt($(this).attr('data-endVal'));
                    theAnimation = new countUp(target, 0, endVal, 0, 2.6, { useEasing : true, useGrouping : true, separator: ' ' });
                    theAnimation.start();
                });
            }
        }
    };

    // datepicker
	yukon_datepicker = {
		p_forms_extended: function() {
			if ( $.isFunction($.fn.datepicker) ) {
				// replace datepicker arrow
				$.fn.datepicker.DPGlobal.template = $.fn.datepicker.DPGlobal.template
				.replace(/\&laquo;/g, '<i class="arrow_carrot-left"></i>')
				.replace(/\&raquo;/g, '<i class="arrow_carrot-right"></i>');
			}

			if ($("#dp_basic").length) {
				$("#dp_basic").datepicker({
					autoclose: true
				});
			}
			if ($("#dp_component").length) {
				$("#dp_component").datepicker({
					autoclose: true
				});
			}
			if ($("#dp_range").length) {
				$("#dp_range").datepicker({
					autoclose: true
				});
			}
			if ($("#dp_inline").length) {
				$("#dp_inline").datepicker();
			}
		}
	};

	// date range picker
	yukon_date_range_picker = {
		p_forms_extended: function() {
			if ($("#drp_time").length) {
				$('#drp_time').daterangepicker({
                    timePicker: true,
                    timePickerIncrement: 30,
                    format: 'MM/DD/YYYY h:mm A',
                    buttonClasses: 'btn btn-sm'
                });
			}
			if ($("#drp_predefined").length) {
				$('#drp_predefined').daterangepicker(
                    {
                        ranges: {
                           'Today': [moment(), moment()],
                           'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
                           'Last 7 Days': [moment().subtract('days', 6), moment()],
                           'Last 30 Days': [moment().subtract('days', 29), moment()],
                           'This Month': [moment().startOf('month'), moment().endOf('month')],
                           'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
                        },
                        startDate: moment().subtract('days', 29),
                        endDate: moment()
                    },
                    function(start, end) {
                        $('#drp_predefined span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                    }
				);
			}
		}
	};

    // datatables
	yukon_datatables = {
		p_plugins_tables_datatable: function() {

            var table = $('#datatable_demo').dataTable({
                "iDisplayLength": 25
            });

            // fixed header
            var oFH = new $.fn.dataTable.FixedHeader(table, {
                "offsetTop": 48
            });
            oFH.fnUpdate();

            // update fixed headers on window resize
            $(window).on("throttledresize", function( event ) {
                oFH._fnUpdateClones( true );
                oFH._fnUpdatePositions();
            })

		}
	};

    // easyPie chart
    yukon_easyPie_chart = {
        p_dashboard: function() {
            if($('.easy_chart_a').length) {
                $('.easy_chart_a').easyPieChart({
                    animate: 2000,
                    size: 90,
                    lineWidth: 4,
                    scaleColor: false,
                    barColor: '#48ac2e',
                    trackColor: '#eee',
                    easing: 'easeOutBounce',
                    onStep: function(from, to, percent) {
                        $(this.el).children('.easy_chart_percent').text(Math.round(percent) + '%');
                    }
                });
            }
            if($('.easy_chart_b').length) {
                $('.easy_chart_b').easyPieChart({
                    animate: 2000,
                    size: 90,
                    lineWidth: 4,
                    scaleColor: false,
                    barColor: '#c0392b',
                    trackColor: '#eee',
                    easing: 'easeOutBounce',
                    onStep: function(from, to, percent) {
                    }
                });
            }
            if($('.easy_chart_c').length) {
                $('.easy_chart_c').easyPieChart({
                    animate: 2000,
                    size: 90,
                    lineWidth: 4,
                    scaleColor: false,
                    barColor: '#4a89dc',
                    trackColor: '#eee',
                    easing: 'easeOutBounce',
                    onStep: function(from, to, percent) {
                    }
                });
            }
        },
        p_pages_user_profile: function() {
            if($('.easy_chart_user_tasks').length) {
				$('.easy_chart_user_tasks').easyPieChart({
					animate: 2000,
					size: 60,
					lineWidth: 3,
					scaleColor: false,
					barColor: '#48ac2e',
					trackColor: '#ddd',
					easing: 'easeOutBounce'
				});
			}
            if($('.easy_chart_user_mails').length) {
				$('.easy_chart_user_mails').easyPieChart({
					animate: 2000,
					size: 60,
					lineWidth: 3,
					scaleColor: false,
					barColor: '#c0392b',
					trackColor: '#ddd',
					easing: 'easeOutBounce',
					onStep: function(from, to, percent) {
						$(this.el).children('.easy_chart_percent_text').html(Math.round(percent) + '%<small>Mails</small>');
					}
				});
			}
            if($('.easy_chart_user_sale').length) {
				$('.easy_chart_user_sale').easyPieChart({
					animate: 2000,
					size: 60,
					lineWidth: 3,
					scaleColor: false,
					barColor: '#4a89dc',
					trackColor: '#ddd',
					easing: 'easeOutBounce',
					onStep: function(from, to, percent) {
						$(this.el).children('.easy_chart_percent').html(Math.round(percent) + '%');
					}
				});
			}
        }
    };

    // footable
    yukon_footable = {
        p_pages_mailbox: function() {
            $('#mailbox_table').footable({
                toggleSelector: " > tbody > tr > td > span.footable-toggle"
            });
        },
        p_plugins_tables_footable: function() {

            $('#footable_demo').footable({
                toggleSelector: " > tbody > tr > td > span.footable-toggle"
            }).on({
                'footable_filtering': function (e) {
                    var selected = $('#userStatus').find(':selected').text();
                    if (selected && selected.length > 0) {
                        e.filter += (e.filter && e.filter.length > 0) ? ' ' + selected : selected;
                        e.clear = !e.filter;
                    }
                }
            });

            $('#clearFilters').click(function(e) {
                e.preventDefault();
                $('#userStatus').val('');
                $('#footable_demo').trigger('footable_clear_filter');
            });

            $('#userStatus').change(function (e) {
                e.preventDefault();
                $('#footable_demo').data('footable-filter').filter( $('#textFilter').val() );
            });

            // clear filters on page load
            $('#textFilter, #userStatus').val('');

        }
    };

    // gmaps
    yukon_gmaps = {
        init: function() {
            // basic google maps
            new GMaps({
                div: '#gmap_basic',
                lat: -12.043333,
                lng: -77.028333
            });

            // with markers
            map_markers = new GMaps({
                el: '#gmap_markers',
                lat: 51.500902,
                lng: -0.124531
            });
            map_markers.addMarker({
                lat: 51.497714,
                lng: -0.12991,
                title: 'Westminster',
                details: {
                    // You can attach additional information, which will be passed to Event object (e) in the events previously defined.
                },
                click: function(e){
                    alert('You clicked in this marker');
                },
                mouseover: function(e){
                    if(console.log) console.log(e);
                }
            });
            map_markers.addMarker({
                lat: 51.500891,
                lng: -0.123347,
                title: 'Westminster Bridge',
                infoWindow: {
                    content: '<div class="infoWindow_content"><p>Westminster Bridge is a road and foot traffic bridge over the River Thames...</p><a href="http://en.wikipedia.org/wiki/Westminster_Bridge" target="_blank">wikipedia</a></div>'
                }
            });

            // static map
            var img_scale = window.devicePixelRatio >= 2 ? '&scale=2' : '';
            var background_size = window.devicePixelRatio >= 2 ? 'background-size: 640px 640px;' : '';

            url = GMaps.staticMapURL({
                size: [640, 640],
                lat: -37.824972,
                lng: 144.958735,
                zoom: 10
            });
            $('#gmap_static').append('<span class="gmap-static" style="height:100%;display:block;background: url('+url+img_scale+') no-repeat 50% 50%;'+background_size+'"><img src="'+url+'" style="visibility:hidden" alt="" /></span>');

            // geocoding
            map_geocode = new GMaps({
                el: '#gmap_geocoding',
                lat: 55.478853,
                lng: 15.117188,
                zoom: 3
            });
            $('#geocoding_form').submit(function (e) {
                e.preventDefault();
                GMaps.geocode({
                    address: $('#gmaps_address').val().trim(),
                    callback: function (results, status) {
                        if (status == 'OK') {
                            var latlng = results[0].geometry.location;
                            map_geocode.setCenter(latlng.lat(), latlng.lng());
                            map_geocode.addMarker({
                                lat: latlng.lat(),
                                lng: latlng.lng()
                            });
                            map_geocode.map.setZoom(15);
                            $('#gmaps_address').val('');
                        }
                    }
                });
            });
        }
    };

    // jBox
    yukon_jBox = {
        p_components_notifications_popups: function() {

            new jBox('Modal', {
                width: 340,
                height: 180,
                attach: $('#jbox_modal_drag'),
                draggable: 'title',
                closeButton: 'title',
                title: 'Click here to drag me around',
                content: 'You can move this modal window'
            });

            new jBox('Confirm', {
                closeButton: false,
                confirmButton: 'Yes',
                cancelButton: 'No',
                _onOpen: function() {
                    // Set the new action for the submit button
                    this.submitButton
                        .off('click.jBox-Confirm' + this.id)
                        .on('click.jBox-Confirm' + this.id, function() {
                            new jBox('Notice', {
                                offset: {
                                    y: 36
                                },
                                content: 'Comment deleted: id=34'
                            });
                            this.close();
                        }.bind(this));
                }
            });
            $('#jbox_n_default').click(function() {
                new jBox('Notice', {
                    offset: {
                        y: 36
                    },
                    stack: false,
                    autoClose: 30000,
                    animation: {
                        open: 'slide:top',
                        close: 'slide:right'
                    },
                    onInit: function () {
                        this.options.content = 'Default notification';
                    }
                });
            });
            $('#jbox_n_audio').click(function() {
                new jBox('Notice', {
                    attributes: {
                        x: 'right',
                        y: 'bottom'
                    },
                    theme: 'NoticeBorder',
                    color: 'green',
                    audio: 'assets/lib/jBox-0.3.0/Source/audio/bling2',
                    volume: '100',
                    stack: false,
                    autoClose: 3000,
                    animation: {
                        open: 'slide:bottom',
                        close: 'slide:left'
                    },
                    onInit: function () {
                        this.options.title = 'Title';
                        this.options.content = 'Notification with audio effect';
                    }
                });
            });
            $('#jbox_n_audio50').click(function() {
                new jBox('Notice', {
                    attributes: {
                        x: 'right',
                        y: 'top'
                    },
                    offset: {
                        y: 36
                    },
                    theme: 'NoticeBorder',
                    color: 'blue',
                    audio: 'assets/lib/jBox-0.3.0/Source/audio/beep2',
                    volume: '60',
                    stack: false,
                    autoClose: 3000,
                    animation: {
                        open: 'slide:top',
                        close: 'slide:right'
                    },
                    onInit: function () {
                        this.options.title = 'Title';
                        this.options.content = 'Volume set to 60%';
                    }
                })
            });

        }
    };

    // listNav
    yukon_listNav = {
        p_pages_user_list: function() {
            $('#user_list').listnav({
                filterSelector: '.ul_lastName',
                includeNums: false,
                removeDisabled: true,
                showCounts: false,
                onClick: function(letter) {
                    $('.countUsers').text($(".listNavShow").length);
                }
            });
        }
    };

    // magnific lightbox
    yukon_magnific = {
        p_components_gallery: function() {
            $('.gallery_grid .img_wrapper').magnificPopup({
                type: 'image',
                gallery:{
                    enabled: true,
                    arrowMarkup: '<i title="%title%" class="el-icon-chevron-%dir% mfp-nav"></i>'
                },
                image: {
                    titleSrc: function(item) {
                        return item.el.attr('title') + '<small>' + item.el.children(".gallery_image_tags").text() + '</small>';
                    }
                },
                removalDelay: 500, //delay removal by X to allow out-animation
                callbacks: {
                    beforeOpen: function() {
                        $('html').addClass('magnific-popup-open');
                        // just a hack that adds mfp-anim class to markup
                        this.st.image.markup = this.st.image.markup.replace('mfp-figure', 'mfp-figure mfp-with-anim');
                        this.st.mainClass = 'mfp-zoom-in';
                    },
                    close: function() {
                        $('html').removeClass('magnific-popup-open');
                    }
                },
                retina: {
                    ratio: 2
                },
                closeOnContentClick: true,
                midClick: true // allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source.
            });
        }
    };

    // masked inputs
    yukon_maskedInputs = {
        p_forms_extended: function() {
            $("#mask_date").inputmask("dd/mm/yyyy",{ "placeholder": "dd/mm/yyyy", showMaskOnHover: false });
            $("#mask_phone").inputmask("mask", {"mask": "(999) 999-9999"});
            $("#mask_plate").inputmask({"mask": "[9-]AAA-999"});
            $("#mask_numeric").inputmask('€ 999.999,99', { numericInput: false });
            $("#mask_mac").inputmask({"mask": "**:**:**:**:**:**"});
            $("#mask_callback").inputmask("mm/dd/yyyy",{ "placeholder": "mm/dd/yyyy", "oncomplete": function(){ alert('Date entered: '+$(this).val()); } });
            $('[data-inputmask]').inputmask();
        }
    };

    // validation (parsley.js)
    yukon_parsley_validation = {
        p_forms_validation: function() {
            $('#form_validation').parsley();
        },
        p_forms_wizard: function() {
            $('#wizard_validation').parsley();
			var thisIndex = 0;
			$.listen('parsley:field:validate', function(e) {
				yukon_steps.setContentHeight('#'+e.$element.closest('div.wizard').attr('id'));
			});
		}
    };

    // qrcode
    yukon_qrcode = {
        p_pages_invoices: function() {
            $('#invoice_qrcode').css({'width': gr_code_data.baseSize / 2, 'height': gr_code_data.baseSize / 2}).qrcode({
                render: 'canvas',
                size: gr_code_data.baseSize,
                text: gr_code_data.qrText
            }).children('img').prop('title', gr_code_data.qrText);
        }
    };

    // rangeSlider
	yukon_rangeSlider = {
		p_forms_extended: function() {
			if ($("#rS_exm_1").length) {
				$("#rS_exm_1").ionRangeSlider({
					min: 0,
					max: 5000,
					from: 1200,
					to: 2450,
					type: 'double',
					prefix: "$",
					maxPostfix: "+",
					prettify: false,
					hasGrid: true
				});
			}
			if ($("#rS_exm_2").length) {
				$("#rS_exm_2").ionRangeSlider({
					min: 1000,
					max: 100000,
					from: 30000,
					to: 90000,
					type: 'double',
					step: 500,
					postfix: " €",
					hasGrid: true
				});
			}
			if ($("#rS_exm_3").length) {
				$("#rS_exm_3").ionRangeSlider({
					min: 0,
					max: 10,
					type: 'single',
					step: 0.1,
					postfix: " carats",
					prettify: false,
					hasGrid: true
				});
			}
			if ($("#rS_exm_4").length) {
				$("#rS_exm_4").ionRangeSlider({
					min: -50,
					max: 50,
					from: 0,
					postfix: "°",
					prettify: false,
					hasGrid: true
				});
			}
			if ($("#rS_exm_5").length) {
				$("#rS_exm_5").ionRangeSlider({
					min: 10000,
					max: 100000,
					step: 100,
					postfix: " km",
					from: 55000,
					hideMinMax: true,
					hideFromTo: false
				});
			}
		}
	};

    // select2
	yukon_select2 = {
		p_forms_extended: function() {
			if ($("#s2_basic").length) {
				$("#s2_basic").select2({
					allowClear: true,
					placeholder: "Select..."
				});
			}
			if ($("#s2_multi").length) {
				$("#s2_multi").select2({
					placeholder: "Select..."
				});
			}
			if($('#s2_tokenization').length) {
				$('#s2_tokenization').select2({
					placeholder: "Select...",
					tags:["red", "green", "blue", "black", "orange", "white"],
					tokenSeparators: [",", " "]
				});
			}
			if($('#s2_ext_value').length) {

				function format(state) {
					if (!state.id) return state.text;
					return '<i class="flag-' + state.id + '"></i>' + state.text;
				}

				$('#s2_ext_value').select2({
					placeholder: "Select Country",
					formatResult: format,
					formatSelection: format,
					escapeMarkup: function(markup) { return markup; }
				}).val("AU").trigger("change");

				$("#s2_ext_us").click(function(e) { e.preventDefault(); $("#s2_ext_value").val("US").trigger("change"); });
				$("#s2_ext_br_gb").click(function(e) { e.preventDefault(); $("#s2_ext_value").val(["JP","PL"]).trigger("change"); });
			}
			if($('#s2_load_data').length) {
				$("#s2_load_data").select2({
					data:[
						{id:0,text:'enhancement'},
						{id:1,text:'bug'},
						{id:2,text:'duplicate'},
						{id:3,text:'invalid'},
						{id:4,text:'wontfix'}
					]
				});
			}
		},
        p_forms_validation: function() {
			if($('#val_select').length) {
				$('#val_select').select2({
					allowClear: true,
					placeholder: "Select..."
				});
			}
		},
        p_forms_wizard: function() {
			if($('#s2_country').length) {
				function format(state) {
					if (!state.id) return state.text;
					return '<i class="flag-' + state.id + '"></i>' + state.text;
				}
				$('#s2_country').select2({
					placeholder: "Select Country",
					formatResult: format,
					formatSelection: format,
					escapeMarkup: function(markup) { return markup; }
				});
			}
			if($('#s2_languages').length) {
				$('#s2_languages').select2({
					placeholder: "Select language",
					tags:["Mandarin", "Spanish", "English", "Hindi", "Arabic", "Portuguese"],
					tokenSeparators: [",", " "]
				});
			}
		}
	};

    // wizard
	yukon_steps = {
		init: function() {
			if ($("#wizard_101").length) {
				// initialize wizard
				$("#wizard_101").steps({
					headerTag: 'h3',
					bodyTag: "section",
					titleTemplate: "<span class=\"title\">#title#</span>",
					enableAllSteps: true,
					enableFinishButton: false,
					transitionEffect: "slideLeft",
					labels: {
						next: "Next <i class=\"fa fa-angle-right\"></i>",
						previous: "<i class=\"fa fa-angle-left\"></i> Previous",
						current: "",
						finish: "Agree"
					},
					onStepChanged: function (event, currentIndex, priorIndex) {
						// adjust wizard height
						yukon_steps.setContentHeight('#wizard_101')
					}
				});
				// set initial wizard height
				yukon_steps.setContentHeight('#wizard_101');
			}
			if ($("#wizard_form").length) {
				var wizard_form = $('#wizard_form');
				// initialize wizard
				wizard_form.steps({
					headerTag: 'h3',
					bodyTag: "section",
					enableAllSteps: true,
					titleTemplate: "<span class=\"title\">#title#</span>",
					transitionEffect: "slideLeft",
					labels: {
						next: "Next Step <i class=\"fa fa-angle-right\"></i>",
						previous: "<i class=\"fa fa-angle-left\"></i> Previous Step",
						current: "",
						finish: "<i class=\"fa fa-check\"></i> Register"
					},
					onStepChanging: function (event, currentIndex, newIndex) {
						var cursentStep = wizard_form.find('.content > .body').eq(currentIndex);
						// check input fields for errors
						cursentStep.find('[data-parsley-id]').each(function() {
							$(this).parsley().validate();
						});

						return cursentStep.find('.parsley-error').length ? false : true;
					},
					onStepChanged: function (event, currentIndex, priorIndex) {
						// adjust wizard height
						yukon_steps.setContentHeight('#wizard_form');
					},
					onFinishing: function (event, currentIndex) {
						var cursentStep = wizard_form.find('.content > .body').eq(currentIndex);
						// check input fields for errors
						cursentStep.find('[data-parsley-id]').each(function() {
							$(this).parsley().validate();
						});

                        return cursentStep.find('.parsley-error').length ? false : true;
					},
					onFinished: function(event, currentIndex) {
						alert("Submitted!");
                        // uncomment the following line to submit form
                        //wizard_form.submit();
					}
				});
				// set initial wizard height
				yukon_steps.setContentHeight('#wizard_form');
            }
        },
		setContentHeight: function($wizard) {
			setTimeout(function() {
				var cur_height = $($wizard).children('.content').children('.body.current').outerHeight();
				$($wizard).find('.content').height(cur_height);
			},0);
		}
	};

    // switchery
    yukon_switchery = {
        init: function() {
            if($('.js-switch').length) {
                var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
                elems.forEach(function(html) {
                    var switchery = new Switchery(html);
                });
            }
            if($('.js-switch-blue').length) {
                var blue = document.querySelector('.js-switch-blue');
                var switchery = new Switchery(blue, { color: '#41b7f1' });
            }
            if($('.js-switch-success').length) {
				var elem = document.querySelector('.js-switch-success');
				var switchery = new Switchery(elem, { color: '#8cc152' });
			}
			if($('.js-switch-warning').length) {
				var elem = document.querySelector('.js-switch-warning');
				var switchery = new Switchery(elem, { color: '#f6bb42' });
			}
			if($('.js-switch-danger').length) {
				var elem = document.querySelector('.js-switch-danger');
				var switchery = new Switchery(elem, { color: '#da4453' });
			}
			if($('.js-switch-info').length) {
				var elem = document.querySelector('.js-switch-info');
				var switchery = new Switchery(elem, { color: '#37bc9b' });
			}
        }
    };

    // textarea autosize
    yukon_textarea_autosize = {
        init: function() {
            if($('.textarea_auto').length) {
                $('.textarea_auto').autosize();
            }
        }
    };

    // maxLength for textareas
    yukon_textarea_maxlength = {
        p_forms_extended: function() {
            if($('#ml_default').length) {
                $('#ml_default').stopVerbosity({
                    limit: 20,
                    existingIndicator: $('#ml_default_indicator')
                });
            }
            if($('#ml_custom').length) {
                $('#ml_custom').stopVerbosity({
                    limit: 32,
                    existingIndicator: $('#ml_custom_indicator'),
                    indicatorPhrase: [
                        'This is a custom indicator phrase.',
                        'This one only counts down. Only', '<span class="label label-primary">[countdown]</span>', 'characters', 'left.'
                    ]
                })
            }
        }
    };

    // multiuploader
    yukon_uploader = {
        p_forms_extended: function() {
            if($('#uploader').length) {
                $("#uploader").pluploadQueue({
                    // General settings
                    runtimes : 'html5,flash,silverlight,html4',
                    url : "/upload",

                    chunk_size : '1mb',
                    rename : true,
                    dragdrop: true,

                    filters : {
                        // Maximum file size
                        max_file_size : '10mb',
                        // Specify what files to browse for
                        mime_types: [
                            {title : "Image files", extensions : "jpg,gif,png"},
                            {title : "Zip files", extensions : "zip"}
                        ]
                    },

                    // Resize images on clientside if we can
                    resize: {
                        width : 200,
                        height : 200,
                        quality : 90,
                        crop: true // crop to exact dimensions
                    },


                    // Flash settings
                    flash_swf_url : 'assets/lib/plupload/js/Moxie.swf',

                    // Silverlight settings
                    silverlight_xap_url : 'assets/lib/plupload/js/Moxie.xap'
                });
            }
        }
    };

    // vector maps
    yukon_vector_maps = {
        p_dashboard: function() {
            if($('#world_map_vector').length) {
                $('#world_map_vector').vectorMap({
                    map: 'world_mill_en',
                    backgroundColor: 'transparent',
                    regionStyle: {
                        initial: {
                            fill: '#c8c8c8'
                        },
                        hover: {
                            "fill-opacity": 1
                        }
                    },
                    series: {
                        regions: [{
                            values: countries_data,
                            scale: ['#58bbdf', '#1c7393'],
                            normalizeFunction: 'polynomial'
                        }]
                    },
                    onRegionLabelShow: function(e, el, code){
                        if(typeof countries_data[code] == 'undefined') {
                            e.preventDefault();
                        } else {
                            var countryLabel = countries_data[code];
                            el.html(el.html()+': '+countryLabel+' visits');
                        }
                    }
                });
            }
        },
        p_plugins_vector_maps: function() {

            // random colors
            var palette = ['#1f77b4', '#3a9add', '#888'];

            function generateColors() {
                var colors = {},
                    key;
                for (key in map_ca.regions) {
                    colors[key] = palette[Math.floor(Math.random() * palette.length)];
                }
                return colors;
            };

            function updateColors() {
                map_ca.series.regions[0].setValues(generateColors());
            };

            $('#updateColors').click(function(e) {
                e.preventDefault();
                updateColors();
            })

            map_ca = new jvm.WorldMap({
                map: 'ca_mill_en',
                container: $('#vmap_canada'),
                backgroundColor: 'transparent',
                series: {
                    regions: [
                        {
                            attribute: 'fill'
                        }
                    ]
                }
            });
            map_ca.series.regions[0].setValues(generateColors());

            // markers on the map
            $('#vmap_markers').vectorMap({
                map: 'world_mill_en',
                backgroundColor: 'transparent',
                scaleColors: ['#c8eeff', '#0071a4'],
                normalizeFunction: 'polynomial',
                hoverColor: false,
                regionStyle: {
                    initial: {
                        fill: '#888'
                    },
                    hover: {
                        "fill-opacity": 1
                    }
                },
                markerStyle: {
                    initial: {
                        fill: '#fff',
                        stroke: '#1f77b4'
                    },
                    hover: {
                        fill: '#13476c',
                        stroke: '#13476c'
                    }
                },
                markers: [
                  {latLng: [41.90, 12.45], name: 'Vatican City'},
                  {latLng: [43.73, 7.41], name: 'Monaco'},
                  {latLng: [-0.52, 166.93], name: 'Nauru'},
                  {latLng: [-8.51, 179.21], name: 'Tuvalu'},
                  {latLng: [43.93, 12.46], name: 'San Marino'},
                  {latLng: [47.14, 9.52], name: 'Liechtenstein'},
                  {latLng: [7.11, 171.06], name: 'Marshall Islands'},
                  {latLng: [17.3, -62.73], name: 'Saint Kitts and Nevis'},
                  {latLng: [3.2, 73.22], name: 'Maldives'},
                  {latLng: [35.88, 14.5], name: 'Malta'},
                  {latLng: [12.05, -61.75], name: 'Grenada'},
                  {latLng: [13.16, -61.23], name: 'Saint Vincent and the Grenadines'},
                  {latLng: [13.16, -59.55], name: 'Barbados'},
                  {latLng: [17.11, -61.85], name: 'Antigua and Barbuda'},
                  {latLng: [-4.61, 55.45], name: 'Seychelles'},
                  {latLng: [7.35, 134.46], name: 'Palau'},
                  {latLng: [42.5, 1.51], name: 'Andorra'},
                  {latLng: [14.01, -60.98], name: 'Saint Lucia'},
                  {latLng: [6.91, 158.18], name: 'Federated States of Micronesia'},
                  {latLng: [1.3, 103.8], name: 'Singapore'},
                  {latLng: [1.46, 173.03], name: 'Kiribati'},
                  {latLng: [-21.13, -175.2], name: 'Tonga'},
                  {latLng: [15.3, -61.38], name: 'Dominica'},
                  {latLng: [-20.2, 57.5], name: 'Mauritius'},
                  {latLng: [26.02, 50.55], name: 'Bahrain'},
                  {latLng: [0.33, 6.73], name: 'São Tomé and Príncipe'}
                ]
              });
        }
    };

	// wysiwg editor
	yukon_wysiwg = {
		p_forms_validation: function() {
			if ($('#val_textarea_message').length) {
				var editor_validate = $('textarea#val_textarea_message').ckeditor();
			}
		},
        p_forms_extended_elements: function() {
			if ($('#wysiwg_editor').length) {
				$('#wysiwg_editor').ckeditor();
			}
		}
	};