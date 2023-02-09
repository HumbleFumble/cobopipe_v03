import shotgun_api3
import pprint

# Setting default fields of interest
HUMAN_USER_FIELDS = [
    "name",
    "sg_status_list",
    "email",
    "permission_rule_set",
    "projects",
    "groups",
]
CLIENT_USER_FIELDS = [
    "name",
    "firstname",
    "lastname",
    "sg_status_list",
    "email",
    "permission_rule_set",
    "projects",
    "groups",
]
API_USER_FIELDS = [
    "firstname",
    "description",
    "id",
    "email",
    "permission_rule_set",
    "projects",
    "lastname",
    "salted_password",
]
PROJECT_FIELDS = ["name", "id", "sg_description", "sg_status", "users", "tank_name", "code"]
EPISODE_FIELDS = [
    "project",
    "code",
    "id",
    "description",
    "sg_status_list",
    "sequences",
]
SEQUENCE_FIELDS = [
    "project",
    "code",
    "id",
    "description",
    "sg_status_list",
    "shots",
    "assets",
]
SHOT_FIELDS = ["project", "code", "id", "sg_status_list", "sg_cut_duration", "assets"]
ASSET_FIELDS = [
    "project",
    "code",
    "id",
    "sg_status_list",
    "sg_asset_type",
    "parents",
    "task_template",
]
TASK_FIELDS = [
    "project",
    "content",
    "id",
    "entity",
    "step",
    "sg_status_list",
    "sg_client_status",
    "task_assignees",
    "task_reviewers",
    "start_date",
    "due_date",
    "duration",
]
VERSION_FIELDS = ["project", "code", "id", "sg_status_list", "user"]
TASK_TEMPLATE_FIELDS = ["id", "code"]

# Creating an API instance
def get_shotgrid(
    url="https://cphbom.shotgrid.autodesk.com/",
    script="cobopipe",
    key="fbda0Jg$zihrnynjqhiaywhic",
):
    return shotgun_api3.Shotgun(url, script_name=script, api_key=key)


def initialize(
    url="https://cphbom.shotgrid.autodesk.com/",
    script="cobopipe",
    key="fbda0Jg$zihrnynjqhiaywhic",
):
    if "shotgrid_api" not in globals():
        global shotgrid_api
        shotgrid_api = get_shotgrid(url=url, script=script, key=key)
    return shotgrid_api


def get_task_templates(fields=TASK_TEMPLATE_FIELDS):
    initialize()
    task_templates = []
    data = shotgrid_api.find("TaskTemplate", filters=[], fields=fields)
    for item in data:
        task_templates.append(TaskTemplate(**item, query=False))
    return task_templates


class HumanUser:
    def __init__(self, fields=HUMAN_USER_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def __getattr__(self, name: str):
        return self.__dict__[f"{name}"]


class ClientUser:
    def __init__(self, fields=CLIENT_USER_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def update(self):
        _update_entity(self)
        self.identity = {"type": self.type, "id": self.id}
    
    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def __getattr__(self, name: str):
        return self.__dict__[f"{name}"]


class ApiUser:
    def __init__(self, fields=API_USER_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.firstname = value
            elif variable == "version":
                self.lastname = value
            elif variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def __getattr__(self, name: str):
        if name == "name":
            return self.firstname
        elif name == "version":
            return self.lastname
        else:
            return self.__dict__[f"{name}"]


class Project:
    def __init__(self, fields=PROJECT_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_users(self, query=True):
        users = []
        for user in self.users:
            users.append(HumanUser(**user, query=query))
        return users

    def get_episodes(self, fields=EPISODE_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "episode",
            fields,
            Episode,
            extra_filters,
            query=query,
        )

    def get_sequences(self, fields=SEQUENCE_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "sequence",
            fields,
            Sequence,
            extra_filters,
            query=query,
        )

    def get_shots(self, fields=SHOT_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "shot",
            fields,
            Shot,
            extra_filters,
            query=query,
        )

    def get_assets(self, fields=ASSET_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "asset",
            fields,
            Asset,
            extra_filters,
            query=query,
        )

    def get_tasks(self, fields=TASK_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "task",
            fields,
            Task,
            extra_filters,
            query=query,
        )

    def get_versions(self, fields=VERSION_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            self.type,
            "version",
            fields,
            Version,
            extra_filters,
            query=query,
        )

    def create_episode(self, code: str, nice_name: str = ""):
        data = {"project": self.identity, "code": code, "description": nice_name}
        episode = shotgrid_api.create("Episode", data)
        return Episode(**episode, query=False)

    def create_asset(
        self, code: str, description: str = "", task_template: object = None
    ):
        data = {"project": self.identity, "code": code, "description": description}
        if task_template:
            data["task_template"] = task_template.identity
        asset = shotgrid_api.create("Asset", data)
        return Asset(**asset, query=False)

    def __getattr__(self, code: str):
        self.__dict__[f"{name}"]


class Episode:
    def __init__(self, fields=EPISODE_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.code = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_sequences(self, query=True):
        sequences = []
        for sequence in self.sequences:
            sequences.append(Sequence(**sequence, query=query))
        return sequences

    def get_shots(self, query=True):
        shots = []
        sequences = self.get_sequences()
        for sequence in sequences:
            shots = shots + sequence.get_shots(query=query)
        return shots

    def get_assets(self, fields=ASSET_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "episodes",
            "asset",
            fields,
            Asset,
            extra_filters,
            query=query,
        )

    def get_tasks(self, fields=TASK_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "task",
            fields,
            Asset,
            extra_filters,
            query=query,
        )

    def get_versions(self, fields=VERSION_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "version",
            fields,
            Version,
            extra_filters,
            query=query,
        )

    def create_sequence(
        self, code: str, description: str = "", task_template: object = None
    ):
        data = {"episode": self.identity, "code": code, "description": description}
        if task_template:
            data["task_template"] = task_template.identity
        sequence = shotgrid_api.create("Sequence", data)
        return Sequence(**sequence, query=False)

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["code"]
        else:
            return self.__dict__[f"{name}"]


class Sequence:
    def __init__(self, fields=SEQUENCE_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.code = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query_shotgrid()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_shots(self, query=True):
        shots = []
        for shot in self.shots:
            shots.append(Shot(**shot, query=query))
        return shots

    def get_assets(self, query=True):
        assets = []
        for asset in self.assets:
            assets.append(Asset(**asset, query=query))
        return assets

    def get_tasks(self, fields=TASK_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "task",
            fields,
            Task,
            extra_filters,
            query=query,
        )

    def get_versions(self, fields=VERSION_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "version",
            fields,
            Version,
            extra_filters,
            query=query,
        )

    def create_shot(
        self, code: str, description: str = "", task_template: object = None
    ):
        data = {"sg_sequence": self.identity, "code": code, "description": description}
        if task_template:
            data["task_template"] = task_template.identity
        shot = shotgrid_api.create("Shot", data)
        return Shot(**shot, query=False)

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["code"]
        else:
            return self.__dict__[f"{name}"]


class Shot:
    def __init__(self, fields=SHOT_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.code = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_assets(self, query=True):
        assets = []
        for asset in self.assets:
            assets.append(Asset(**asset, query=query))
        return assets

    def get_tasks(self, fields=TASK_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "task",
            fields,
            Task,
            extra_filters,
            query=query,
        )

    def get_versions(self, fields=VERSION_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "version",
            fields,
            Version,
            extra_filters,
            query=query,
        )

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["code"]
        else:
            return self.__dict__[f"{name}"]


class Asset:
    def __init__(self, fields=ASSET_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.code = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def update(self):
        _update_entity(self)
        self.identity = {"type": self.type, "id": self.id}
    
    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_tasks(self, fields=TASK_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "task",
            fields,
            Task,
            extra_filters,
            query=query,
        )

    def get_versions(self, fields=VERSION_FIELDS, extra_filters=[], query=True):
        return _get_entity(
            self.identity,
            "entity",
            "version",
            fields,
            Version,
            extra_filters,
            query=query,
        )

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["code"]
        else:
            return self.__dict__[f"{name}"]


class Task:
    def __init__(self, fields=TASK_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.content = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def update(self):
        _update_entity(self)
        self.identity = {"type": self.type, "id": self.id}
    
    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_parent(self, query=True):
        _type = self.entity['type']
        _name = self.entity['name']
        _id = self.entity['id']
        _class = globals()[_type]
        return _class(name=_name, id=_id, query=query)

    def get_versions(self, query=True):
        versions = []
        for version in self.sg_versions:
            versions.append(Version(**version, query=query))

    def get_artists(self):
        artists = []
        for user in self.task_assignees:
            artists.append(HumanUser(**user))
        return artists

    def get_reviewers(self):
        reviewers = []
        for user in self.task_reviewers:
            reviewers.append(HumanUser(**user))
        return reviewers

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["content"]
        else:
            return self.__dict__[f"{name}"]


class Version:
    def __init__(self, fields=VERSION_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.code = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)

    def get_artist(self):
        return HumanUser(**self.user)

    def get_task(self):
        return Task(**self.sg_task)

    def __getattr__(self, name: str):
        if name == "name":
            return self.__dict__["content"]
        else:
            return self.__dict__[f"{name}"]


class TaskTemplate:
    def __init__(self, fields=TASK_TEMPLATE_FIELDS, query=True, **kwargs):
        if not kwargs:
            raise ValueError("Missing identifying keyword arguments like name or id")

        self.fields = fields
        self.type = self.__class__.__name__

        for variable, value in kwargs.items():
            if variable == "name":
                self.content = value
            if variable in self.fields:
                exec(f"self.{variable} = {repr(value)}")

        initialize()
        if query:
            self.query()
        if "id" in self.__dict__.keys():
            self.identity = {"type": self.type, "id": self.id}

    def query(self):
        _query_entity(self)
        self.identity = {"type": self.type, "id": self.id}

    def __repr__(self):
        return _repr_entity(self)

    def __str__(self):
        return _str_entity(self)
        return reviewers

    def __getattr__(self, name: str):
        if name == "name":
            return self.code
        else:
            return self.__dict__[f"{name}"]


def _repr_entity(self):
    return f"<ShotGrid.{self.__class__.__name__} object>"


def _str_entity(self):
    _string = f"\n<ShotGrid.{self.__class__.__name__} object>\n"
    for variable, value in self.__dict__.items():
        if variable in self.fields:
            _string = _string + f"{variable:<10} \t{pprint.pformat(value)}\n"
    return _string


def _get_entity(
    source_identity,
    source_type,
    target_type,
    fields,
    return_class,
    extra_filters=[],
    query=True,
):
    filters = [[source_type.lower(), "is", source_identity]]
    filters = filters + extra_filters
    data = shotgrid_api.find(target_type.capitalize(), filters=filters, fields=fields)
    objects = []
    for entity in data:
        objects.append(return_class(query=query, **entity))
    return objects


def _query_entity(self):
    filters = []
    for variable, value in self.__dict__.items():
        if variable in self.fields:
            if value:
                filters.append([variable, "is", value])

    if not filters:
        raise ValueError("Missing filter data")

    # print(f"\n\nfilters: {filters}\nfields: {self.fields}\n\n")
    data = shotgrid_api.find(self.type, filters=filters, fields=self.fields)
    if not data:
        return
    for variable, value in data[0].items():
        exec(f"self.{variable} = {repr(value)}")

def _update_entity(self):
    data = {}
    for variable, value in self.__dict__.items():
        if not variable in self.fields:
            continue
        if variable in ['id', 'type']:
            continue
        data[variable] = value

    shotgrid_api.update(self.type, self.id, data)

if __name__ == "__main__":
    # project = Project(name="Lego Friends - Wildbrain")
    task = Task(id=6224)
    shot = task.get_parent(query=False)
    print(shot)