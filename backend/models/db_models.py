import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator, CHAR
import json

from backend.db.database import Base

class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

class RoleEnum(str, PyEnum):
    recruiter = "recruiter"
    admin = "admin"
    candidate = "candidate"

class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.candidate, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CandidateAnalysis(Base):
    __tablename__ = "candidate_analysis"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    candidate_name = Column(String, nullable=False)
    resume_filename = Column(String, nullable=False)
    target_role = Column(String, nullable=False)
    final_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    shortlist_decision = Column(String, nullable=False)
    shap_data = Column(String, nullable=True)  # JSON text
    skill_gap_data = Column(String, nullable=True)  # JSON text
    fairness_data = Column(String, nullable=True)  # JSON text
    ai_provider_used = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BatchAnalysis(Base):
    __tablename__ = "batch_analysis"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    batch_name = Column(String, nullable=False)
    candidate_ids = Column(String, nullable=False)  # JSON text
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    version_string = Column(String, unique=True, index=True, nullable=False)
    training_date = Column(DateTime, default=datetime.utcnow)
    ndcg_score = Column(Float, nullable=True)
    auc_score = Column(Float, nullable=True)
    num_training_samples = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
