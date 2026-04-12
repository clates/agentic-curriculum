import networkx as nx
import re
from typing import List, Dict, Any, Optional


class CASEGraphV2:
    """
    A standalone logic engine for building and analyzing curriculum dependency graphs
    based on the CASE (Competency and Academic Standards Exchange) framework.
    """

    def __init__(self, items: List[Dict[str, Any]], associations: List[Dict[str, Any]]):
        self.graph = nx.DiGraph()
        self.items = {item["identifier"]: item for item in items}
        self._build_graph(items, associations)

    def _build_graph(self, items: List[Dict[str, Any]], associations: List[Dict[str, Any]]):
        # 1. Add all items as nodes
        for item in items:
            # If title is not provided (e.g. from standards table), extract it
            if "title" not in item:
                item["title"] = self.extract_title(item.get("fullStatement", ""))
            self.graph.add_node(item["identifier"], **item)

        # 2. Add associations as edges
        for assoc in associations:
            assoc_type = assoc.get("associationType")
            origin = assoc.get("originNodeIdentifier")
            dest = assoc.get("destinationNodeIdentifier")

            if not origin or not dest or origin not in self.items or dest not in self.items:
                continue

            if assoc_type == "isChildOf":
                # Parent -> Child
                self.graph.add_edge(dest, origin, type="hierarchy")
            elif assoc_type == "precedes":
                # Precursor -> Successor
                self.graph.add_edge(origin, dest, type="dependency")

        self._deduplicate_nodes()
        self._inject_continuity_edges()
        self._filter_containers()

    def _deduplicate_nodes(self):
        """
        Merges nodes that are semantically identical.
        """
        duplicates = {}
        for node_id, data in self.graph.nodes(data=True):
            key = (
                data.get("humanCodingScheme"),
                data.get("fullStatement"),
                data.get("educationLevel"),
            )
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(node_id)

        for _key, ids in duplicates.items():
            if len(ids) <= 1:
                continue
            canonical = ids[0]
            others = ids[1:]
            for other in others:
                for u, _v, data in list(self.graph.in_edges(other, data=True)):
                    if u != canonical and not self.graph.has_edge(u, canonical):
                        self.graph.add_edge(u, canonical, **data)
                for _u, v, data in list(self.graph.out_edges(other, data=True)):
                    if v != canonical and not self.graph.has_edge(canonical, v):
                        self.graph.add_edge(canonical, v, **data)
                if other in self.graph:
                    self.graph.remove_node(other)

    def _filter_containers(self):
        HIDDEN_TYPES = {"Grade Band", "Course", "Subject"}
        HIDDEN_STATEMENTS = {
            "English Language Arts Courses with Adopted Standards",
            "Elementary English Language Arts K-5",
            "Middle School English Language Arts 6-8",
            "High School English Language Arts 9-12",
            "Additional English Language Arts Courses",
            "Retired English Language Arts Courses",
        }

        nodes_to_remove = [
            n
            for n, d in self.graph.nodes(data=True)
            if d.get("CFItemType") in HIDDEN_TYPES or d.get("fullStatement") in HIDDEN_STATEMENTS
        ]

        for node in nodes_to_remove:
            in_edges = list(self.graph.in_edges(node, data=True))
            out_edges = list(self.graph.out_edges(node, data=True))
            for u, _, in_data in in_edges:
                for _, v, out_data in out_edges:
                    edge_type = out_data.get("type", "dependency")
                    is_implicit = in_data.get("implicit", False) or out_data.get("implicit", False)
                    if not self.graph.has_edge(u, v):
                        self.graph.add_edge(u, v, type=edge_type, implicit=is_implicit)
            if node in self.graph:
                self.graph.remove_node(node)

    def _inject_continuity_edges(self):
        """
        Injects implicit dependency edges between standards with the same signature
        across consecutive grade levels.
        """
        grade_map = {}
        for node_id, data in self.graph.nodes(data=True):
            raw_grade = data.get("educationLevel")
            if raw_grade is None:
                continue
            try:
                if isinstance(raw_grade, list):
                    grade_str = raw_grade[0]
                else:
                    grade_str = str(raw_grade).split(",")[0]

                if grade_str.upper() in ("KG", "K"):
                    grade_num = 0
                else:
                    # Legacy standards use 0, 1, 2... integers
                    grade_num = int(float(grade_str))
            except (ValueError, IndexError):
                continue

            if grade_num not in grade_map:
                grade_map[grade_num] = {}

            code = data.get("humanCodingScheme")
            if code:
                sig_id = re.sub(r"^([0-9]{1,2}|K|KG|PK)\.", "", code)
                if sig_id != code:
                    if sig_id not in grade_map[grade_num]:
                        grade_map[grade_num][sig_id] = node_id

            title = data.get("title")
            if title:
                sig_title = f"TITLE:{title}"
                if sig_title not in grade_map[grade_num]:
                    grade_map[grade_num][sig_title] = node_id

        sorted_grades = sorted(grade_map.keys())
        for i in range(1, len(sorted_grades)):
            prev_grade = sorted_grades[i - 1]
            curr_grade = sorted_grades[i]
            for sig, curr_node in grade_map[curr_grade].items():
                if sig in grade_map[prev_grade]:
                    prev_node = grade_map[prev_grade][sig]
                    if not self.graph.has_edge(prev_node, curr_node):
                        self.graph.add_edge(prev_node, curr_node, type="dependency", implicit=True)

    @staticmethod
    def extract_title(full_statement: str) -> str:
        if not full_statement:
            return "Untitled"
        clean_stmt = full_statement.replace("**", "")
        domain_match = re.search(r"DOMAIN:\s*(.*?)(?:\(|$)", clean_stmt)
        if domain_match:
            return domain_match.group(1).strip()
        idea_match = re.search(r"BIG IDEA:\s*(.*?)(?:\*\*|$)", clean_stmt)
        if idea_match:
            return idea_match.group(1).strip()
        prefix_match = re.match(r"^(.*?):", clean_stmt)
        if prefix_match:
            title = prefix_match.group(1).strip()
            if len(title) > 3:
                return title
        sentences = clean_stmt.split(".")
        if sentences:
            title = sentences[0].strip()
            if 3 < len(title) < 80:
                return title
        return (clean_stmt[:47] + "...").strip()

    def get_readiness_states(self, mastered_identifiers: List[str]) -> Dict[str, str]:
        states = {}
        mastered_set = set(mastered_identifiers)
        try:
            sorted_nodes = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            sorted_nodes = list(self.graph.nodes())

        for node in sorted_nodes:
            if node in mastered_set:
                states[node] = "mastered"
                continue
            deps = [
                u
                for u, v, d in self.graph.in_edges(node, data=True)
                if d.get("type") == "dependency"
            ]
            deps_met = all(d in mastered_set for d in deps)
            parents = [
                u
                for u, v, d in self.graph.in_edges(node, data=True)
                if d.get("type") == "hierarchy"
            ]
            parent_met = not parents or any(p in mastered_set for p in parents)
            if deps_met and parent_met:
                states[node] = "ready"
            else:
                states[node] = "locked"
        return states

    def get_pruned_nodes(self, mastered_identifiers: List[str], depth: int = 1) -> List[str]:
        mastered_set = set(mastered_identifiers)
        states = self.get_readiness_states(mastered_identifiers)
        ready_nodes = [node for node, state in states.items() if state == "ready"]
        nodes_to_keep = set(mastered_set)
        nodes_to_keep.update(ready_nodes)
        frontier = set(ready_nodes)
        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                successors = [v for u, v, d in self.graph.out_edges(node, data=True)]
                next_frontier.update(successors)
            nodes_to_keep.update(next_frontier)
            frontier = next_frontier
        final_nodes = set(nodes_to_keep)
        for node in nodes_to_keep:
            curr = node
            visited = set()
            while curr in self.graph and curr not in visited:
                visited.add(curr)
                parents = [
                    u
                    for u, v, d in self.graph.in_edges(curr, data=True)
                    if d.get("type") == "hierarchy"
                ]
                if not parents:
                    break
                final_nodes.update(parents)
                curr = parents[0]
        return list(final_nodes)

    def export_for_visualization(
        self, mastered_identifiers: Optional[List[str]] = None, prune: bool = False
    ):
        mastered_list = mastered_identifiers or []
        states = self.get_readiness_states(mastered_list)
        if prune:
            keep_ids = set(self.get_pruned_nodes(mastered_list))
        else:
            keep_ids = set(self.graph.nodes())
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if node_id not in keep_ids:
                continue
            nodes.append(
                {
                    "id": node_id,
                    "data": {
                        "label": data.get("title") or data.get("humanCodingScheme") or "Standard",
                        "idLabel": data.get("humanCodingScheme"),
                        "fullStatement": data.get("fullStatement"),
                        "state": states.get(node_id, "locked"),
                        "educationLevel": data.get("educationLevel"),
                        "itemType": data.get("CFItemType"),
                    },
                    "type": "standard",
                }
            )
        edges = []
        for u, v, data in self.graph.edges(data=True):
            if u in keep_ids and v in keep_ids:
                edges.append(
                    {
                        "id": f"{u}-{v}",
                        "source": u,
                        "target": v,
                        "type": data.get("type"),
                        "implicit": data.get("implicit", False),
                    }
                )
        return {"nodes": nodes, "edges": edges}


def load_from_db(db_path: str, subject_keyword: Optional[str] = None) -> CASEGraphV2:
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    keyword = subject_keyword
    if subject_keyword == "Math":
        keyword = "Mathematics"

    # 1. Try CASE data first
    if keyword:
        cursor.execute(
            "SELECT identifier FROM case_items WHERE fullStatement LIKE ?", (f"%{keyword}%",)
        )
        start_nodes = [row["identifier"] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT identifier FROM case_items")
        start_nodes = [row["identifier"] for row in cursor.fetchall()]

    if start_nodes:
        # Recursively find descendants in CASE hierarchy
        all_related_ids = set(start_nodes)
        frontier = list(start_nodes)
        while frontier:
            next_frontier = []
            for i in range(0, len(frontier), 900):
                chunk = frontier[i : i + 900]
                placeholders = ",".join(["?"] * len(chunk))
                cursor.execute(
                    f"SELECT originNodeIdentifier FROM case_associations WHERE destinationNodeIdentifier IN ({placeholders}) AND associationType='isChildOf'",
                    chunk,
                )
                children = [row[0] for row in cursor.fetchall()]
                for c in children:
                    if c not in all_related_ids:
                        all_related_ids.add(c)
                        next_frontier.append(c)
            frontier = next_frontier

        ids_list = list(all_related_ids)
        items = []
        for i in range(0, len(ids_list), 900):
            chunk = ids_list[i : i + 900]
            placeholders = ",".join(["?"] * len(chunk))
            cursor.execute(f"SELECT * FROM case_items WHERE identifier IN ({placeholders})", chunk)
            items.extend([dict(row) for row in cursor.fetchall()])

        associations = []
        for i in range(0, len(ids_list), 450):
            chunk = ids_list[i : i + 450]
            placeholders = ",".join(["?"] * len(chunk))
            cursor.execute(
                f"SELECT * FROM case_associations WHERE originNodeIdentifier IN ({placeholders}) OR destinationNodeIdentifier IN ({placeholders})",
                chunk + chunk,
            )
            associations.extend([dict(row) for row in cursor.fetchall()])

        seen_assoc = set()
        unique_assoc = []
        for a in associations:
            if a["identifier"] not in seen_assoc:
                if (
                    a["originNodeIdentifier"] in all_related_ids
                    and a["destinationNodeIdentifier"] in all_related_ids
                ):
                    unique_assoc.append(a)
                    seen_assoc.add(a["identifier"])

        conn.close()
        return CASEGraphV2(items, unique_assoc)

    # 2. Fallback to standards table
    if subject_keyword:
        cursor.execute("SELECT * FROM standards WHERE subject = ?", (subject_keyword,))
        rows = cursor.fetchall()
        if rows:
            items = []
            for r in rows:
                desc = r["description"] or ""
                items.append(
                    {
                        "identifier": r["standard_id"],
                        "fullStatement": desc,
                        "humanCodingScheme": r["standard_id"],
                        "educationLevel": str(r["grade_level"]),
                        "CFItemType": "Standard",
                        "title": desc[:60] if desc else r["standard_id"],
                    }
                )
            conn.close()
            return CASEGraphV2(items, [])

    conn.close()
    return CASEGraphV2([], [])


if __name__ == "__main__":
    DB_PATH = "curriculum.db"
    graph = load_from_db(DB_PATH, "Math")
    print(f"Loaded fallback graph with {len(graph.graph.nodes)} nodes.")
