from pip._vendor.requests import Session

from .compat import (
    get_dist_from_abstract_dist,
    get_package_finder,
    get_requirement_preparer,
    is_dir_url,
    is_file_url,
    is_vcs_url,
    parse_requirements,
)


def link_req_to_str(req):
    url = req.link.url
    if req.editable:
        return "-e " + url
    else:
        return url


class RequirementsParser:
    def __init__(self, req_tracker):
        self.session = Session()
        self.finder = get_package_finder(self.session)
        self.preparer = get_requirement_preparer(
            self.finder, self.session, req_tracker
        )

    def _get_local_deps(self, req):
        abstract_dist = self.preparer(req)
        dist = get_dist_from_abstract_dist(abstract_dist)
        return dist.requires(req.extras)

    def _process_requirement(self, req):
        ext_reqs, loc_reqs = [], []
        if req.link:
            if is_vcs_url(req.link):
                # TODO: Is this needed or even supported?
                raise NotImplementedError(
                    "Requirement `{}` is not in a supported format".format(
                        str(req)
                    )
                )
            elif is_file_url(req.link):
                if is_dir_url(req.link):
                    loc_reqs.append(link_req_to_str(req))
                    for subreq in self._get_local_deps(req):
                        ext_reqs.append(str(subreq))
                else:
                    # TODO: Is this needed or even supported?
                    raise NotImplementedError(
                        "Requirement `{}` is not in a supported format".format(
                            str(req)
                        )
                    )
            else:
                ext_reqs.append(link_req_to_str(req))
        else:
            ext_reqs.append(str(req.req))

        return ext_reqs, loc_reqs

    def parse(self, reqs_filepath):
        ext_reqs, loc_reqs = [], []
        for raw_req in parse_requirements(reqs_filepath, session=self.session):
            ext_subreqs, loc_subreqs = self._process_requirement(raw_req)
            ext_reqs.extend(ext_subreqs)
            loc_reqs.extend(loc_subreqs)
        return ext_reqs, loc_reqs
