# яркий перелив (серый → почти чёрный) с !important
BG_STYLE = """
body::before{
    content:'';
    position:fixed!important;
    inset:0!important;
    z-index:-1!important;
    background:radial-gradient(circle at 30% 30%,
                #404349 0%, #2e3036 45%, #15161b 100%) !important;
    background-size:800% 800%!important;
    animation:bgShift 5s ease-in-out infinite!important;
}
@keyframes bgShift{
    0%  {background-position:0 0}
    50% {background-position:100% 100%}
    100%{background-position:0 0}
}
"""