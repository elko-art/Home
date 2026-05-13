// 动态搜索引擎联想推荐 - 根据当前选中的搜索引擎切换联想来源
var currentSearchEngine = 'google';

$(function() {
    // 初始化：读取当前选中的搜索引擎
    updateSearchEngine();

    // 监听搜索引擎选择变化
    $(document).on('change', 'input[name="type2"]', function() {
        updateSearchEngine();
    });

    // 更新当前搜索引擎
    function updateSearchEngine() {
        var selectedId = $('input[name="type2"]:checked').attr('id') || 'm_type-google1';
        if (selectedId.includes('google')) {
            currentSearchEngine = 'google';
        } else if (selectedId.includes('bing')) {
            currentSearchEngine = 'bing';
        } else if (selectedId.includes('duckduckgo')) {
            currentSearchEngine = 'duckduckgo';
        } else {
            currentSearchEngine = 'none';
        }
    }

    // 监听搜索框输入，根据当前引擎请求联想
    $(document).on('input', '#m_search-text', function() {
        var keywords = $(this).val();
        if (keywords == '' || keywords.length < 1) { 
            $('#word').empty().hide();
            return;
        }
        
        if (currentSearchEngine === 'google') {
            requestGoogleSuggestions(keywords);
        } else if (currentSearchEngine === 'bing') {
            requestBingSuggestions(keywords);
        } else if (currentSearchEngine === 'duckduckgo') {
            requestDuckDuckGoSuggestions(keywords);
        } else {
            $('#word').empty().hide();
        }
    });

    // Google 联想
    function requestGoogleSuggestions(keywords) {
        $.ajax({
            url: 'https://www.google.com/complete/search?client=chrome&q=' + encodeURIComponent(keywords),
            dataType: 'jsonp',
            jsonp: 'callback',
            timeout: 3000,
            success: function(res) {
                if (res && res[1]) {
                    displaySuggestions(res[1].slice(0, 8));
                } else {
                    $('#word').empty().hide();
                }
            },
            error: function() {
                $('#word').empty().hide();
            }
        });
    }

    // Bing 联想
    function requestBingSuggestions(keywords) {
        $.ajax({
            url: 'https://www.bing.com/osjson.aspx?query=' + encodeURIComponent(keywords),
            dataType: 'json',
            timeout: 3000,
            success: function(res) {
                if (res && res[1]) {
                    displaySuggestions(res[1].slice(0, 8));
                } else {
                    $('#word').empty().hide();
                }
            },
            error: function() {
                $('#word').empty().hide();
            }
        });
    }

    // DuckDuckGo 联想
    function requestDuckDuckGoSuggestions(keywords) {
        $.ajax({
            url: 'https://duckduckgo.com/ac?q=' + encodeURIComponent(keywords),
            dataType: 'json',
            timeout: 3000,
            success: function(res) {
                if (res && res.length > 0) {
                    var suggestions = res.slice(0, 8).map(function(item) {
                        return item.phrase || '';
                    }).filter(function(item) { return item; });
                    displaySuggestions(suggestions);
                } else {
                    $('#word').empty().hide();
                }
            },
            error: function() {
                $('#word').empty().hide();
            }
        });
    }

    // 显示联想列表
    function displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            $('#word').empty().hide();
            return;
        }
        
        $('#word').empty().show();
        $.each(suggestions, function(i, suggestion) {
            var rankColor = ['#f54545', '#ff8547', '#ffac38'];
            var color = rankColor[i] || '#999';
            var html = '<li><span style="color: #fff; background: ' + color + ';">' + (i + 1) + '</span>' + suggestion + '</li>';
            $('#word').append(html);
        });
        $('#word').css('display', 'block');
    }

    // 点击联想项
    $(document).on('click', '#word li', function() {
        var word = $(this).text().replace(/^[0-9]/, '').trim();
        $('#m_search-text').val(word);
        $('#word').empty().hide();
        $('.super-search-fm').submit();
    });

    // 点击其他地方隐藏联想
    $(document).on('click', '.io-grey-mode, .panel-body', function() {
        $('#word').empty().hide();
    });
})
