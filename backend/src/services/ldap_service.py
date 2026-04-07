"""
LDAP/Active Directory Authentication Service
For on-premise STBank internal network integration
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Try to import ldap3, but don't fail if not installed
try:
    from ldap3 import SUBTREE, ALL

    LDAP3_AVAILABLE = True
except ImportError:
    LDAP3_AVAILABLE = False
    SUBTREE = "SUBTREE"  # Placeholder
    ALL = "ALL"


@dataclass
class LDAPUser:
    """LDAP User data"""

    username: str
    email: str
    display_name: str
    department: Optional[str] = None
    branch: Optional[str] = None
    phone: Optional[str] = None
    groups: List[str] = None

    def __post_init__(self):
        if self.groups is None:
            self.groups = []


class LDAPService:
    """
    LDAP/AD Authentication for on-premise deployment
    Supports: OpenLDAP, Microsoft Active Directory
    """

    def __init__(self, config: dict = None):
        """
        Initialize LDAP service with configuration

        Required config:
        - LDAP_SERVER: ldap://192.168.x.x or ldaps://
        - LDAP_BASE_DN: DC=stbank,DC=la
        - LDAP_USER_DN: CN=admin,DC=stbank,DC=la
        - LDAP_PASSWORD: admin password
        """
        self.config = config or {}
        self.server = self.config.get("LDAP_SERVER", "")
        self.base_dn = self.config.get("LDAP_BASE_DN", "dc=stbank,dc=la")
        self.user_dn = self.config.get("LDAP_USER_DN", "")
        self.password = self.config.get("LDAP_PASSWORD", "")
        self.use_ssl = self.config.get("LDAP_USE_SSL", True)
        self.enabled = self.config.get("LDAP_ENABLED", False)

        # Group mappings
        self.group_map = {
            "Sales Rep": ["sales", "rep", "tellers"],
            "Branch Manager": ["manager", "branch_head"],
            "Compliance Officer": ["compliance", "audit"],
            "IT Admin": ["it_admin", "system_admin", " administrators"],
        }

    def authenticate(self, username: str, password: str) -> Optional[LDAPUser]:
        """
        Authenticate user against LDAP/AD
        Returns user info if successful, None if failed
        """
        if not self.enabled:
            logger.warning("LDAP authentication is disabled")
            return None

        if not LDAP3_AVAILABLE:
            logger.error("ldap3 package not installed. Run: pip install ldap3")
            return None

        try:
            from ldap3 import Server, Connection

            # Connect to LDAP server
            server = Server(self.server, use_ssl=self.use_ssl, get_info=ALL)

            # Try to bind with user credentials
            user_dn = self._get_user_dn(username)

            if not user_dn:
                logger.warning(f"User not found in LDAP: {username}")
                return None

            # Bind as user to verify password
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)

            if conn.bound:
                # Get user info
                user_info = self._get_user_info(conn, user_dn)
                conn.unbind()
                return user_info

            conn.unbind()
            return None

        except ImportError:
            logger.error("ldap3 package not installed. Run: pip install ldap3")
            return None
        except Exception as e:
            logger.error(f"LDAP authentication error: {str(e)}")
            return None

    def _get_user_dn(self, username: str) -> Optional[str]:
        """Construct user DN from username"""
        # Try common LDAP patterns
        patterns = [
            f"uid={username},ou=users,{self.base_dn}",
            f"cn={username},ou=users,{self.base_dn}",
            f"sAMAccountName={username},{self.base_dn}",
            f"mail={username},{self.base_dn}",
        ]

        # For testing without LDAP, return a mock
        if not self.enabled:
            return patterns[0]

        # In production, would search LDAP
        return patterns[0]

    def _get_user_info(self, conn, user_dn: str) -> LDAPUser:
        """Extract user information from LDAP"""
        try:
            conn.search(
                search_base=user_dn,
                search_filter="(objectClass=*)",
                search_scope=SUBTREE,
                attributes=[
                    "cn",
                    "mail",
                    "displayName",
                    "department",
                    "telephoneNumber",
                    "memberOf",
                ],
            )

            if conn.entries:
                entry = conn.entries[0]

                groups = []
                if hasattr(entry, "memberOf"):
                    for group in entry.memberOf.values:
                        groups.append(str(group).split(",")[0].replace("CN=", ""))

                return LDAPUser(
                    username=str(entry.cn) if hasattr(entry, "cn") else "",
                    email=str(entry.mail) if hasattr(entry, "mail") else "",
                    display_name=(
                        str(entry.displayName) if hasattr(entry, "displayName") else ""
                    ),
                    department=(
                        str(entry.department) if hasattr(entry, "department") else None
                    ),
                    phone=(
                        str(entry.telephoneNumber)
                        if hasattr(entry, "telephoneNumber")
                        else None
                    ),
                    groups=groups,
                )
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")

        # Return basic user from DN
        cn = user_dn.split(",")[0].replace("CN=", "").replace("uid=", "")
        return LDAPUser(username=cn, email=f"{cn}@stbank.la", display_name=cn)

    def get_user_role(self, ldap_user: LDAPUser) -> str:
        """Map LDAP groups to application roles"""
        user_groups = [g.lower() for g in ldap_user.groups]

        for role, keywords in self.group_map.items():
            for keyword in keywords:
                if any(keyword in g for g in user_groups):
                    return role

        # Default role based on department
        if ldap_user.department:
            dept = ldap_user.department.lower()
            if "sales" in dept or "marketing" in dept:
                return "sales_rep"
            if "it" in dept or "technology" in dept:
                return "it_admin"
            if "compliance" in dept or "audit" in dept:
                return "compliance"

        return "sales_rep"  # Default

    def sync_user_from_ldap(self, username: str, db_session) -> Optional[dict]:
        """
        Sync user from LDAP to local database
        Returns user dict or None
        """
        from ..models.user import User
        from ..services.auth_service import AuthService

        # This would normally authenticate with LDAP to get full info
        # For now, create a placeholder

        # Check if user exists
        user = db_session.query(User).filter(User.email.ilike(f"%{username}%")).first()

        if user:
            # Update role if needed
            return {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "branch_id": user.branch_id,
            }

        return None


class LDAPAuthService:
    """
    High-level LDAP authentication service
    Handles hybrid auth: LDAP + local fallback
    """

    def __init__(self):
        from ..config.settings import settings

        self.ldap_service = LDAPService(
            {
                "LDAP_SERVER": settings.LDAP_SERVER,
                "LDAP_BASE_DN": settings.LDAP_BASE_DN,
                "LDAP_USER_DN": settings.LDAP_USER_DN,
                "LDAP_PASSWORD": settings.LDAP_PASSWORD,
                "LDAP_USE_SSL": settings.LDAP_USE_SSL,
                "LDAP_ENABLED": settings.LDAP_ENABLED,
            }
        )

    def login(self, username: str, password: str, db_session) -> Optional[dict]:
        """
        Try LDAP authentication first, then local fallback
        Returns user dict if successful
        """
        # Try LDAP first
        if self.ldap_service.enabled:
            ldap_user = self.ldap_service.authenticate(username, password)

            if ldap_user:
                role = self.ldap_service.get_user_role(ldap_user)

                return {
                    "username": ldap_user.username,
                    "email": ldap_user.email,
                    "display_name": ldap_user.display_name,
                    "role": role,
                    "department": ldap_user.department,
                    "auth_method": "ldap",
                }

        # Fallback to local authentication
        return None

    def get_ldap_config(self) -> dict:
        """Get LDAP configuration for frontend"""
        return {
            "enabled": self.ldap_service.enabled,
            "server": self.ldap_service.server if self.ldap_service.enabled else None,
            "base_dn": self.ldap_service.base_dn if self.ldap_service.enabled else None,
        }
