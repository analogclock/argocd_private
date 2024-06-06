module.exports = {
    "env": {
        "browser": true,
        "es6": true,
        "node": true
    },
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
        "tsconfigRootDir": __dirname,
        "project": "tsconfig.json",
        "sourceType": "module"
    },
    "plugins": [
        "eslint-plugin-import",
        "@angular-eslint/eslint-plugin",
        "@typescript-eslint"
    ],
    "rules": {
        "@angular-eslint/component-class-suffix": "error",
        "@angular-eslint/component-selector": [
            "error",
            {
                "type": [
                    "element",
                    "attribute"
                ],
                "prefix": "zf",
                "style": "kebab-case"
            }
        ],
        "@angular-eslint/directive-class-suffix": "error",
        "@angular-eslint/directive-selector": [
            "error",
            {
                "type": "attribute",
                "prefix": "zf",
                "style": "camelCase"
            }
        ],
        "@angular-eslint/no-host-metadata-property": "error",
        "@angular-eslint/no-input-rename": "error",
        "@angular-eslint/no-inputs-metadata-property": "error",
        "@angular-eslint/no-output-rename": "error",
        "@angular-eslint/no-outputs-metadata-property": "error",
        "@angular-eslint/use-lifecycle-interface": "error",
        "@angular-eslint/use-pipe-transform-interface": "error",
        "@typescript-eslint/consistent-type-definitions": "error",
        "@typescript-eslint/dot-notation": "off",
        "@typescript-eslint/explicit-member-accessibility": [
            "error",
            {
                "accessibility": "explicit",
                "overrides": {
                    "accessors": "explicit",
                    "constructors": "off",
                    "parameterProperties": "explicit"
                }
            }
        ],
        "@typescript-eslint/indent": ["error", 4],
        "@typescript-eslint/member-delimiter-style": [
            "error",
            {
                "multiline": {
                    "delimiter": "comma",
                    "requireLast": false
                },
                "singleline": {
                    "delimiter": "comma",
                    "requireLast": false
                },
                "overrides": {
                    "interface": {
                        "multiline": {
                            "delimiter": "semi",
                            "requireLast": true
                        },
                        "singleline": {
                            "delimiter": "semi",
                            "requireLast": true
                        }
                    }
                }
            }
        ],
        "@typescript-eslint/member-ordering": [
            "error",
            {
                "default": {
                    "memberTypes": [
                        "public-static-field",
                        "protected-static-field",
                        "private-static-field",

                        "public-static-method",
                        "protected-static-method",
                        "private-static-method",

                        "public-instance-field",
                        "protected-instance-field",
                        "private-instance-field",

                        "constructor",

                        "public-instance-method",
                        "protected-instance-method",
                        "private-instance-method"
                    ]
                }
            }
        ],
        "@typescript-eslint/naming-convention": [
            "error",
            {
                "selector": ["default"],
                "format": ["camelCase", "UPPER_CASE", "snake_case"],
                "leadingUnderscore": "allowSingleOrDouble",
                "trailingUnderscore": "allowSingleOrDouble"
            },
            {
                "selector": ["default"],
                "modifiers": ["const"],
                "format": ["camelCase", "UPPER_CASE", "snake_case"]
            },
            {
                "selector": ["typeLike"],
                "format": ["PascalCase"]
            },
            {
                "selector": ["property"],
                "modifiers": ["readonly"],
                "format": ["PascalCase", "camelCase"]
            },
            {
                "selector": ["enumMember"],
                "format": ["UPPER_CASE"]
            }
        ],
        "@typescript-eslint/no-empty-function": "off",
        "@typescript-eslint/no-empty-interface": "error",
        "@typescript-eslint/no-inferrable-types": "off",
        "@typescript-eslint/no-unused-expressions": "error",
        "@typescript-eslint/prefer-function-type": "error",
        "@typescript-eslint/no-shadow": "error",
        "@typescript-eslint/quotes": [
            "error",
            "single"
        ],
        "@typescript-eslint/semi": [
            "error",
            "always"
        ],
        "@typescript-eslint/type-annotation-spacing": "error",
        "@typescript-eslint/unified-signatures": "error",
        "brace-style": [
            "error",
            "1tbs",
            {
                "allowSingleLine": true
            }
        ],
        "curly": "error",
        "eol-last": "error",
        "eqeqeq": [
            "error",
            "smart"
        ],
        "guard-for-in": "error",
        "id-blacklist": [
            "error",
            "any",
            "Number",
            "number",
            "String",
            "string",
            "Boolean",
            "boolean",
            "Undefined",
            "undefined"
        ],
        "id-match": "error",
        "import/no-deprecated": "warn",
        "max-len": [
            "error",
            {
                "code": 140
            }
        ],
        "no-bitwise": "off",
        "no-caller": "error",
        "no-console": "error",
        "no-debugger": "error",
        "no-empty": "off",
        "no-eval": "error",
        "no-fallthrough": "error",
        "no-new-wrappers": "error",
        "no-redeclare": "error",
        "no-restricted-imports": "error",
        "no-shadow": "off",
        "no-throw-literal": "error",
        "no-trailing-spaces": "error",
        "no-unused-labels": "error",
        "no-var": "error",
        "prefer-const": "error",
        "radix": "error",
        "spaced-comment": [
            "error",
            "always",
            {
                "markers": [
                    "/"
                ]
            }
        ]
    }
};
