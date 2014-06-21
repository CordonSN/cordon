// -----
//      Parsing URL to create direct image
// -----

function url_as_image(url, post_id) {

    $("<img>", {
        src: url,
        //error: function() { alert(url + ': ' + false); },
        load: function() { $("#post-" + post_id + "-content").append('<hr />').append('<img "' + post_id + '" class="img-responsive" src="' + url + '" />'); }
        });

    } // function

function urls_as_image(content, post_id) {

    urls = content.match(/\b(http|https)?(:\/\/)?(\S*)\.(\w{2,4})\b/ig);
    if (urls){
        for (var i = 0, il = urls.length; i < il; i++) {
            url_as_image(urls[i], post_id);
            } // for
        } // if

    // ----- Return content
    return content

    } // function

// -----
//      Parsing URL to create direct videos
// -----

function url_as_youtube_video(video_id, post_id) {

    $("#post-" + post_id + "-content").append('<hr />').append('<div class="responsive-video"><iframe width="560" height="315" src="//www.youtube.com/embed/' + video_id + '" frameborder="0" allowfullscreen=""></iframe></div>');

    } // function

function url_as_vimeo_video(video_id, post_id) {

    $("#post-" + post_id + "-content").append('<hr />').append('<div class="responsive-video"><iframe src="//player.vimeo.com/video/' + video_id + '" width="560" height="315" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>');

    }

function urls_as_video(content, post_id) {

    // ----- Youtube Parsing
    url = content.match(/https?:\/\/(?:www\.)?(?:youtube\.com\/watch(?:\?v=|\?.+?&v=)|youtu\.be\/)([a-z0-9_-]+)/i);
    if (url != null) {
        url_as_youtube_video(url[1], post_id);
        } // if

    // ----- Vimeo Parsing
    url = content.match(/https?:\/\/(?:www\.)?vimeo\.com.+?(\d+)/i);
    if (url != null) {
        url_as_vimeo_video(url[1], post_id);
        } // if

    // ----- Daily Motion Parsing
    // url = content.match(/https?:\/\/(?:www\.)?(?:dai\.ly\/|dailymotion\.com\/(?:.+?video=|(?:video|hub)\/))([a-z0-9]+)/i);
    //if (url != null) {
    //  url_as_daily_motion_video(url[1], post_id);
    //  } // if

    // ----- Facebook Parsing
    // url = content.match(/https?:\/\/(?:www\.)?facebook\.com\/photo\.php(?:\?v=|\?.+?&v=)(\d+)/i);
    //if (url != null) {
    //  url_as_facebook_video(url[1], post_id);
    //  } // if

    // ----- Return content
    return content

    } // function

function prettify_content(content, post_id){

    var tmp_content = content

    tmp_content = urls_as_image(tmp_content, post_id);
    tmp_content = urls_as_video(tmp_content, post_id);
    return urlify(tmp_content);

    }
