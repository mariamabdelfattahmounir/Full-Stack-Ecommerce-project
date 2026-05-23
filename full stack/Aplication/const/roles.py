from app.core.roles import (
    Role,
)


ADMIN_ROLES = {
    Role.ADMIN,
}


STAFF_ROLES = {
    Role.ADMIN,
}


CUSTOMER_ROLES = {
    Role.CUSTOMER,
}


ALL_ROLES = {
    Role.ADMIN,
    Role.CUSTOMER,
}


ROLE_HIERARCHY = {

    Role.ADMIN: 100,

    Role.CUSTOMER: 1,
}


ROLE_DISPLAY_NAMES = {

    Role.ADMIN: "Administrator",

    Role.CUSTOMER: "Customer",
}
