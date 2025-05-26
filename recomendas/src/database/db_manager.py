import os
import pandas as pd
from sqlalchemy import create_engine, text, Column, Integer, String, Numeric, DateTime, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID 
from sqlalchemy.orm import sessionmaker, declarative_base, relationship 
import uuid
from datetime import datetime
import logging 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dinel:dan@localhost:5432/recomendas_db")
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
  
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    interests = Column(ARRAY(String), default=[])
    price_preference = Column(String, nullable=True)
    product_specific_preferences = Column(JSONB, default={})
    password_hash = Column(String, nullable=True)

    feedbacks = relationship("Feedback", backref="user_rel", cascade="all, delete-orphan")
    interactions = relationship("Interaction", backref="user_rel", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', name='{self.name}', email='{self.email}')>"

    def to_dict(self):
  
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "interests": self.interests,
            "price_preference": self.price_preference,
            "product_specific_preferences": self.product_specific_preferences,
            "password_hash": self.password_hash
        }


class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    price = Column(Numeric, nullable=True)
    features = Column(ARRAY(String), default=[])
    style = Column(String, nullable=True)
    genre = Column(ARRAY(String), default=[])
    color = Column(ARRAY(String), default=[])
    size = Column(ARRAY(String), default=[])
    author = Column(String, nullable=True)
    material = Column(String, nullable=True)
    performance_score = Column(Integer, nullable=True)
    camera_score = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    attributes = Column(JSONB, default={})
    link = Column(String, nullable=True)

    feedbacks = relationship("Feedback", backref="product_rel", cascade="all, delete-orphan")
    interactions = relationship("Interaction", backref="product_rel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(product_id='{self.product_id}', name='{self.name}')>"

    def to_dict(self):

        return {
            "id": str(self.id),
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "brand": self.brand,
            "price": float(self.price) if self.price is not None else None,
            "features": self.features,
            "style": self.style,
            "genre": self.genre,
            "color": self.color,
            "size": self.size,
            "author": self.author,
            "material": self.material,
            "performance_score": self.performance_score,
            "camera_score": self.camera_score,
            "description": self.description,
            "attributes": self.attributes,
            "link": self.link 
        }


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(String, ForeignKey('products.product_id'), nullable=False)
    rating = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    comment = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "comment": self.comment
        }


class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(String, ForeignKey('products.product_id'), nullable=False)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "product_id": self.product_id,
            "type": self.type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class Category(Base):
    __tablename__ = 'categories'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True) 
    parent_id = Column(String, ForeignKey('categories.id'), nullable=True)
    type = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "type": self.type
        }

class DBManager:
    def __init__(self, database_url=None):
        self.database_url = database_url if database_url else DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        logging.info(f"DBManager inicializado. Conectando a: {self.database_url}")
     
        self.create_tables()

    def create_tables(self):
   
        try:
   
            Base.metadata.create_all(self.engine)
            logging.info("Tabelas do banco de dados criadas/verificadas com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar tabelas: {e}")
            raise

    def get_session(self):
   
        return self.Session()

    def clear_all_tables(self):
 
        logging.info("Iniciando a limpeza de todas as tabelas...")
        session = self.get_session()
        try:
       
            session.execute(text("TRUNCATE TABLE interactions CASCADE;"))
            session.execute(text("TRUNCATE TABLE feedback CASCADE;"))
            session.execute(text("TRUNCATE TABLE products CASCADE;"))
            session.execute(text("TRUNCATE TABLE users CASCADE;"))
            session.execute(text("TRUNCATE TABLE categories CASCADE;"))
            session.commit()
            logging.info("Todas as tabelas foram limpas com sucesso.")
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao limpar tabelas: {e}")
            raise
        finally:
            session.close()

    def get_user_by_name(self, name):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(name=name).first()
            return user
        except Exception as e:
            logging.error(f"Erro ao buscar usuário por nome '{name}': {e}")
            return None
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user
        except Exception as e:
            logging.error(f"Erro ao buscar usuário por user_id '{user_id}': {e}")
            return None
        finally:
            session.close()

    def add_user(self, user_data):
        session = self.get_session()
        try:
            new_user = User(
                user_id=user_data['user_id'],
                name=user_data['name'],
                email=user_data['email'],
                interests=user_data.get('interests', []),
                price_preference=user_data.get('price_preference'),
                product_specific_preferences=user_data.get('product_specific_preferences', {}),
                password_hash=user_data.get('password_hash'),
                created_at=user_data.get('created_at', datetime.now())
            )
            session.add(new_user)
            session.commit()
            logging.info(f"Usuário '{new_user.name}' ({new_user.user_id}) adicionado com sucesso.")
            return new_user
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao adicionar usuário '{user_data.get('email')}': {e}")
            return None
        finally:
            session.close()

    def update_user(self, user_id, updates):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                for key, value in updates.items():
                    setattr(user, key, value)
                session.commit()
                logging.info(f"Usuário '{user_id}' atualizado com sucesso.")
            return user
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao atualizar usuário '{user_id}': {e}")
            return None
        finally:
            session.close()

    def get_all_users(self):
        session = self.get_session()
        try:
            users = session.query(User).all()
            return users
        except Exception as e:
            logging.error(f"Erro ao buscar todos os usuários: {e}")
            return []
        finally:
            session.close()

    def get_all_products(self):
        session = self.get_session()
        try:
            products = session.query(Product).all()
            return products
        except Exception as e:
            logging.error(f"Erro ao buscar todos os produtos: {e}")
            return []
        finally:
            session.close()

    def get_product_by_id(self, product_id):
        session = self.get_session()
        try:
            product = session.query(Product).filter_by(product_id=product_id).first()
            return product
        except Exception as e:
            logging.error(f"Erro ao buscar produto por ID '{product_id}': {e}")
            return None
        finally:
            session.close()

    def get_product_by_name(self, name):
        session = self.get_session()
        try:
            product = session.query(Product).filter_by(name=name).first()
            return product
        except Exception as e:
            logging.error(f"Erro ao buscar produto por nome '{name}': {e}")
            return None
        finally:
            session.close()

    def add_product(self, product_data):
        session = self.get_session()
        try:
            price_value = product_data.get('price')
            if price_value is not None:
                price_value = float(price_value)

            new_product = Product(
                product_id=product_data['product_id'],
                name=product_data['name'],
                category=product_data.get('category'),
                brand=product_data.get('brand'),
                price=price_value,
                features=product_data.get('features', []),
                style=product_data.get('style'),
                genre=product_data.get('genre', []),
                color=product_data.get('color', []),
                size=product_data.get('size', []),
                author=product_data.get('author'),
                material=product_data.get('material'),
                performance_score=product_data.get('performance_score'),
                camera_score=product_data.get('camera_score'),
                description=product_data.get('description'),
                attributes=product_data.get('attributes', {}),
                link=product_data.get('link')
            )
            session.add(new_product)
            session.commit()
            logging.info(f"Produto '{new_product.name}' ({new_product.product_id}) adicionado com sucesso.")
            return new_product
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao adicionar produto '{product_data.get('name')}': {e}")
            return None
        finally:
            session.close()

    def add_feedback(self, feedback_data):
        session = self.get_session()
        try:
            new_feedback = Feedback(
                user_id=feedback_data['user_id'],
                product_id=feedback_data['product_id'],
                rating=feedback_data['rating'],
                comment=feedback_data.get('comment'),
                timestamp=feedback_data.get('timestamp', datetime.now())
            )
            session.add(new_feedback)
            session.commit()
            logging.info(f"Feedback adicionado para user '{feedback_data['user_id']}' e product '{feedback_data['product_id']}'.")
            return new_feedback
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao adicionar feedback: {e}")
            return None
        finally:
            session.close()

    def get_feedback_by_user_id(self, user_id):
        session = self.get_session()
        try:
            feedback = session.query(Feedback).filter_by(user_id=user_id).all()
            return feedback
        except Exception as e:
            logging.error(f"Erro ao buscar feedback para user '{user_id}': {e}")
            return []
        finally:
            session.close()

    def get_all_feedback(self):
        session = self.get_session()
        try:
            feedback = session.query(Feedback).all()
            return feedback
        except Exception as e:
            logging.error(f"Erro ao buscar todos os feedbacks: {e}")
            return []
        finally:
            session.close()

    def add_interaction(self, interaction_data):
        session = self.get_session()
        try:
            new_interaction = Interaction(
                user_id=interaction_data['user_id'],
                product_id=interaction_data['product_id'],
                type=interaction_data['type'],
                timestamp=interaction_data.get('timestamp', datetime.now())
            )
            session.add(new_interaction)
            session.commit()
            logging.info(f"Interação tipo '{interaction_data['type']}' adicionada para user '{interaction_data['user_id']}' e product '{interaction_data['product_id']}'.")
            return new_interaction
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao adicionar interação: {e}")
            return None
        finally:
            session.close()

    def get_all_interactions(self):
        session = self.get_session()
        try:
            interactions = session.query(Interaction).all()
            return interactions
        except Exception as e:
            logging.error(f"Erro ao buscar todas as interações: {e}")
            return []
        finally:
            session.close()

    def add_category(self, category_data):
        session = self.get_session()
        try:
    
            existing_category = session.query(Category).filter_by(id=category_data['id']).first()
            if existing_category:
                logging.info(f"Categoria com ID '{category_data['id']}' já existe, pulando adição.")
                return existing_category

            new_category = Category(
                id=category_data['id'],
                name=category_data['name'],
                parent_id=category_data.get('parent_id'),
                type=category_data['type']
            )
            session.add(new_category)
            session.commit()
            logging.info(f"Categoria '{new_category.name}' ({new_category.id}) adicionada com sucesso.")
            return new_category
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao adicionar categoria '{category_data.get('name')}': {e}")
            return None
        finally:
            session.close()

    def get_all_categories(self):
        session = self.get_session()
        try:
            categories = session.query(Category).all()
            return categories
        except Exception as e:
            logging.error(f"Erro ao buscar todas as categorias: {e}")
            return []
        finally:
            session.close()

    def get_category_by_id(self, category_id):
        session = self.get_session()
        try:
            category = session.query(Category).filter_by(id=category_id).first()
            return category
        except Exception as e:
            logging.error(f"Erro ao buscar categoria por ID '{category_id}': {e}")
            return None
        finally:
            session.close()

    def get_category_by_name(self, name):
        session = self.get_session()
        try:
            category = session.query(Category).filter_by(name=name).first()
            return category
        except Exception as e:
            logging.error(f"Erro ao buscar categoria por nome '{name}': {e}")
            return None
        finally:
            session.close()

    def update_user_interests(self, user_id, new_interests):

        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.interests = new_interests
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar interesses do usuário {user_id}: {e}")
            return False
        finally:
            session.close()

    def load_data_into_df(self, table_name):
        session = self.get_session()
        df = pd.DataFrame()
        try:
            if table_name == 'users':
                data = session.query(User).all()
                df = pd.DataFrame([u.to_dict() for u in data])
            elif table_name == 'products':
                data = session.query(Product).all()
                df = pd.DataFrame([p.to_dict() for p in data])
            elif table_name == 'feedback':
                data = session.query(Feedback).all()
                df = pd.DataFrame([f.to_dict() for f in data])
            elif table_name == 'interactions':
                data = session.query(Interaction).all()
                df = pd.DataFrame([i.to_dict() for i in data]) 
            elif table_name == 'categories': 
                data = session.query(Category).all()
                df = pd.DataFrame([c.to_dict() for c in data]) 
            else:
                logging.warning(f"Tabela '{table_name}' não reconhecida para carregar em DataFrame.")
                return pd.DataFrame()
    
            
            return df
        except Exception as e:
            logging.error(f"Erro ao carregar dados da tabela '{table_name}' para DataFrame: {e}")
            return pd.DataFrame()
        finally:
            session.close()