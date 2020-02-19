import math


def create_input_pair(key, val):
    if val in ["false", "False"]:
        pair = ""
    else:
        prefix = "-" if len(key) == 1 else "--"
        value = "" if val in ["true", "True"] else f" {val}"
        pair = f"{prefix}{key}{value}"
    return pair


# TODO this is dirty! break it into small functions and add numpy style docstring.
def df_to_vw_format(
    df,
    vwcmd,
    target=None,
    tag=None,
    namespace=None,
    base=None,
    importance=None,
    task=None,
    use_binary_label=False,
    class_cost=None,
):
    """
    Convert pandas dataframe to a list of strings of format:
    [Label] [Importance] [Base] [Tag]|Namespace1 Features |Namespace2 Features ...

    For Cost Sensitive One Against All (csoaa) muliclass problem, the output format is
    as per https://github.com/VowpalWabbit/vowpal_wabbit/wiki/Cost-Sensitive-One-Against-All-(csoaa)-multi-class-example#difference-from-other-vw-formats

    """
    all_cols = df.columns.tolist()
    formatted_data = []
    cols_with_ns = []
    cols_without_ns = []

    reverse_namespace = dict()
    ns_names = []
    class_map = {}
    multiclass_map = {}
    target_label = ""
    if target:
        unique_targets = sorted(df[target].unique())
        if use_binary_label:
            if not len(unique_targets) == 2:
                raise InputError(
                    f"use_binary_label is set to True, but number of unique targets {unique_targets} are more than two"
                )
            else:
                class_map[unique_targets[0]] = -1
                class_map[unique_targets[1]] = 1
        else:
            for idx, value in enumerate(unique_targets):
                class_map[value] = idx + 1

    if "csoaa" in vwcmd:
        multiclass = int(vwcmd["csoaa"])
    else:
        multiclass = None
    if multiclass:
        col_list = []
        if target:
            for col in class_cost:
                if col.split("_")[0] in ["Cost"]:
                    col_list.append(col.split("_")[1])
            col_list = sorted(col_list)
            for idx, value in enumerate(col_list):
                multiclass_map[value] = idx + 1
            for idx in range(multiclass):
                target_label += f"{idx+1}:" + "{} "
        else:
            # TODO add support to have only specified target values for each example
            for idx in range(multiclass):
                target_label += f"{idx+1} "

    if namespace:
        ns_names = namespace.keys()
        for key, value in namespace.items():
            cols_with_ns.extend(value)
        cols_with_ns = list(set(cols_with_ns))
        for key, value in namespace.items():
            for col in value:
                if col in reverse_namespace.keys():
                    reverse_namespace[col].extend([key])
                else:
                    reverse_namespace[col] = [key]
    cols_without_ns = list(
        set(all_cols)
        - set(
            [target, tag, base, importance]
            + cols_with_ns
            + ([class_cost] if class_cost is None else class_cost)
        )
    )

    for _, row in df.iterrows():
        ns_part = ""
        feature_part = ""
        all_features_part = ""
        incomplete_row = ""
        extra_part = f""
        if target:
            if multiclass:
                label_values = []
                for col_name, value in multiclass_map.items():
                    label_values.insert(value, row["Cost_" + col_name])
                target_label = target_label.format(*label_values)
            else:
                target_label = class_map[row[target]]
            extra_part += f"{target_label} "
        else:
            if multiclass:
                extra_part += f"{target_label} "

        if not multiclass:
            if importance:
                extra_part += f"{row[importance]} "
            if base:
                extra_part += f"{row[base]} "
        if tag:
            extra_part += f"'{row[tag]} "
        for ns in ns_names:
            all_features_part = ""
            feature_part = ""
            ns_part = f" |{ns}"
            for colname, val in row[namespace[ns]].iteritems():
                if isinstance(val, str):
                    feature_part = f"{val.replace(':','').replace('|', '')}"
                elif isinstance(val, int) or isinstance(val, float):
                    if not math.isnan(val):
                        feature_part = f"{colname.replace(':', '_').replace('|', '_')}:{val}"
                    else:
                        continue
                else:
                    feature_part = f"{val.replace(':', '').replace('|', '')}"
                all_features_part = all_features_part + " " + feature_part

            incomplete_row = incomplete_row + ns_part + all_features_part

        all_features_part = ""
        feature_part = ""
        for idx, value in row[cols_without_ns].iteritems():
            if isinstance(value, str):
                feature_part = f"{value.replace(':','').replace('|', '')}"
            elif isinstance(value, int) or isinstance(value, float):
                if not math.isnan(value):
                    feature_part = (
                        f"{idx.replace(':', '_').replace('|', '_')}:{value}"
                    )
                else:
                    continue
            else:
                feature_part = f"{value.replace(':', '').replace('|', '')}"
            all_features_part = all_features_part + " " + feature_part

        incomplete_row = incomplete_row + (
            (" |" + all_features_part) if all_features_part.strip() else ""
        )
        complete_row = extra_part + incomplete_row
        formatted_data.append(complete_row)
    return formatted_data
