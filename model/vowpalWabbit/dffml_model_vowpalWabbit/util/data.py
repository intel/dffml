import math


def df_to_vw_format(
    df, target=None, tag=None, namespace=None, base=None, importance=None
):
    # [Label] [Importance] [Base] [Tag]|Namespace Features |Namespace Features...
    all_cols = df.columns.tolist()
    formatted_data = []
    cols_with_ns = []
    cols_without_ns = []

    reverse_namespace = dict()
    ns_names = []
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
        set(all_cols) - set([target, tag, base, importance] + cols_with_ns)
    )

    for _, row in df.iterrows():
        ns_part = ""
        feature_part = ""
        all_features_part = ""
        incomplete_row = ""
        extra_part = f""
        if target:
            extra_part += f"{row[target]} "
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
