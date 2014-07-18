def get_cache_key(request):
    req = dict(request.REQUEST)
    req.pop('_','')
    if request.user.is_authenticated():
        uid = request.user.id
    else:
        uid = -1
    return ("%s-%s-%s" % (request.META['PATH_INFO'], str(req), uid)).replace(" ", "")
