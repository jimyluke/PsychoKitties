from flask import jsonify
from pymysql import OperationalError

from . import db
from .models import Kitty
def search_database(args):
    page = args.get('page', 1,type=int)
    sort = args.get('sort', "DESC")
    sort_by = args.get('sort_by', "rarity")
    collection = args.get('collection', "kitty")
    query = args.get('query',"")
    orderby= Kitty.Score.desc()
    if sort_by == "rarity" and sort =="ASC":
        orderby = Kitty.Score
    elif sort_by == "id" and sort =="DESC":
        orderby = Kitty.ID.desc()
    elif sort_by == "id" and sort =="ASC":
        orderby = Kitty.ID
    queryNum = ''.join(char for char in str(query) if char.isdigit())
    likedQuery = f"%{queryNum}%"
    try:
        hits = db.session.query(Kitty)\
            .filter(Kitty.collection==collection) \
            .filter(Kitty.name.like(likedQuery)) \
            .order_by(orderby)\
            .paginate(page, per_page=12)
        results = {
            "results": hits.items,
            "pagination": {
                "count": hits.total,
                "page": page,
                "per_page": 12,
                "pages": hits.pages,
            },
        }
        return jsonify(results), 200
    except OperationalError as e:
        print(e)
        pass
