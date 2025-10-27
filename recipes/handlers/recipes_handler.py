from django.core.cache import cache


# TODO: Implement caching Manager or something to centrilize caching logic
def get_cached_object(key: str) -> object:
    """
    Retrieves an object from the cache using the provided key.
    If the object is not found in the cache, it returns None.
    """
    return cache.get(key)

def set_cached_object(key: str, value, timeout=None) -> tuple:
    """
    Sets an object in the cache with the provided key and value.
    If a timeout is specified, it will be used; otherwise, the default timeout will be used.
    """
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        return (False, str(e))
    return (True, '')



def invalidate_recipe_cache(recipe_id=None) -> dict:
    """
    Invalidates the recipe cache.
    """
    try:
        if recipe_id:
            cache.delete(recipe_id)
        cache.delete('recipe_list_queryset')
    except Exception as e:
        return {'status': 'Cache invalidation failed', 'error': str(e)}
    return {'status': 'Cache invalidated'}


   
