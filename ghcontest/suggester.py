#!/usr/bin/python

class Suggestions(object):

    def __init__(self, user):
        self.user = user
        self.suggested_repos = {}

    def could_add(self, repo):
        return repo not in self.user.watching

    def add(self, repo, weight):
        if self.could_add(repo):
            if repo not in self.suggested_repos:
                self.suggested_repos[repo] = weight
            else:
                self.suggested_repos[repo] += weight

    def top_ten(self):

        def cmp_repos(r1, r2):
            if r1[1] == r2[1]:
#                if abs(r1[0].popularity - r2[0].popularity) <= 5:
#                    return cmp(self.user.lang_pref_similarity(r1[0]),
#                            self.user.lang_pref_similarity(r2[0]))
                return cmp(r1[0].popularity, r2[0].popularity)
            else:
                return cmp(r1[1], r2[1])

        suggested_repos = self.suggested_repos.items()
        suggested_repos.sort(reverse=True, cmp=cmp_repos)
        top_ten = [x[0] for x in suggested_repos]

        return top_ten[:10]

    def __len__(self):
        return len(self.suggested_repos)

PARENT = 4
ANCESTOR = 4
USER = 2
CHILD = 2
SIMILAR = 1
SUPERPROJECT = 1

# just padding if we don't have enough
POPULAR = 0


def add_parents(suggestions, target_user):
    parents = [repo.forked_from for repo in target_user.watching \
            if repo.forked_from != None]
    for parent in parents:
        suggestions.add(parent, PARENT)

def add_ancestors(suggestions, target_user):
    parents = [repo.forked_from for repo in target_user.watching \
            if repo.forked_from != None]
    for parent in parents:
        for ancestor in parent.ancestors:
            suggestions.add(ancestor, ANCESTOR)

def add_watched_owners(suggestions, target_user):
    watched_owners = [x.owner for x in target_user.watching]
    watched_owners = set(watched_owners)
    owned_by_watched_users = set()
    for watched_owner in watched_owners:
        owned_by_watched_users.update(watched_owner.owns)
    owned_by_watched_users = [x for x in owned_by_watched_users]
    for repo in owned_by_watched_users:
        suggestions.add(repo, USER)

def add_children(suggestions, target_user):
    for parent_repo in target_user.watching:
        for repo in parent_repo.forked_by:
            suggestions.add(repo, CHILD)

def add_repos_from_similar_users(suggestions, target_user):
    repos = set()
    users = set()
    for repo in target_user.watching:
        for user in repo.watched_by:
            if user != target_user:
                users.add(user)
    for user in users:
        for repo in user.watching:
            repos.add(repo)
    for repo in repos:
        suggestions.add(repo, SIMILAR)


def add_superprojects(suggestions, target_user, superprojects):
    for watching in target_user.watching:
        for superproject in superprojects.keys():
            if superproject in watching.name.lower():
                for repo in superprojects[superproject]:
                    if superproject in repo.name.lower():
#                        if not target_user.related_to_watching(repo):
                        suggestions.add(repo, SUPERPROJECT)
                break

def suggest_repos(repos, popular_repos, users, target_user, superprojects):
    suggestions = Suggestions(target_user)

    add_parents(suggestions, target_user)
    add_ancestors(suggestions, target_user)
    add_watched_owners(suggestions, target_user)
    add_children(suggestions, target_user)
    add_repos_from_similar_users(suggestions, target_user)
#    add_superprojects(suggestions, target_user, superprojects)


    # pad with popular repos if we don't have 10 already
    if len(suggestions) < 10:
        fav_langs = set(target_user.favourite_langs)
        for popular_repo in popular_repos:
            if not suggestions.could_add(popular_repo):
                continue
            elif len(fav_langs) > 0 and len(popular_repo.lang_names) > 0:
                lang_names = popular_repo.lang_names
                if len(fav_langs.intersection(lang_names)) < 1:
                    continue

            suggestions.add(popular_repo, POPULAR)
            if len(suggestions) >= 10:
                break

    return suggestions.top_ten()
