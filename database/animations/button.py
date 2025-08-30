# градиент-перелив кнопок, всё с !important
BTN_STYLE = """
@keyframes btnShift{
    0%  {background-position:0 0}
    50% {background-position:130% 0}
    100%{background-position:0 0}
}

/* активные кнопки */
.btn:not(.disabled),
button:not([disabled]),
.payment-btn{
    background:linear-gradient(115deg,#5a5d64 0%,#7a7d84 50%,#5a5d64 100%) !important;
    background-size:260% 100%!important;
    color:#fff!important;
    border:none!important;
    animation:btnShift 3s linear infinite!important;
    transition:filter .2s,transform .2s!important;
}
.btn:not(.disabled):hover,
button:not([disabled]):hover,
.payment-btn:hover{
    filter:brightness(1.2)!important;
    transform:translateY(-2px)!important;
}

/* отключённая */
.btn.disabled{
    background:#555!important;
    color:#ccc!important;
    border:none!important;
}
"""