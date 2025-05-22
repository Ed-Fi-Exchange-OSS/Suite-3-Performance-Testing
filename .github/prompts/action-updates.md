#fetch https://raw.githubusercontent.com/Ed-Fi-Alliance-OSS/Ed-Fi-Actions/refs/heads/main/action-allowedlist/approved.json

The `approved.json` file has like the following:

```json
[
  {
    "actionLink": "actions/checkout",
    "actionVersion": "8ade135a41bc03ea155e62e844d188df1ea18608",
    "tag": "v4.1.0",
    "deprecated": true
  },
  {
    "actionLink": "actions/checkout",
    "actionVersion": "b4ffde65f46336ab88eb53be808477a3936bae11",
    "tag": "v4.1.1"
  },
  {
    "actionLink": "actions/checkout",
    "actionVersion": "11bd71901bbe5b1630ceea73d27597364c9af683",
    "tag": "v4.2.2"
  },
]
```

Read and parse this JSON file. Sort it by `actionLink` and `tag`.

For each YAML file in `.github/workflows/*`, find the lines with `uses` and extract the `actions/<actionLink>@<actionVersion> # <tag>`. Match the `<actionLink>` from the `uses` statement to the latest `actionLink` from the `approved.json`. If the `<tag>` and `tag` do not match, then replace the `<actionVersion>` and `<tag>` in the `uses` line with the matched values from `approved.json`. Then write this change to the YAML file.

<!-- This reusable prompt could be useful elsewhere. It did the trick. But probably more efficient to write a script to do this work for better repeat results. Next step then is to modify this prompt to have it create a script. -->
