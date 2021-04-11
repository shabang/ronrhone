module FamilySelector exposing (main)

import Browser
import Data.Animal exposing (Animal)
import Data.Family as Family exposing (Family)
import Date exposing (Date)
import DatePicker exposing (DateEvent(..), defaultSettings)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as Decode
import Request.FamilyCandidates as FamilyCandidates



-- MAIN


main : Program Flags Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


type alias Flags =
    { animals : List Animal
    , url : String
    }


type alias Model =
    { dateDebutPicker : DatePicker.DatePicker
    , date_debut : Maybe Date
    , animals : List Animal
    , selectedAnimals : List Animal
    , families : List Family
    , url : String
    }


init : Flags -> ( Model, Cmd Msg )
init flags =
    let
        ( datePicker, datePickerCmd ) =
            DatePicker.init
    in
    ( { dateDebutPicker = datePicker
      , date_debut = Nothing
      , animals = flags.animals
      , selectedAnimals = []
      , families = []
      , url = flags.url
      }
    , Cmd.map SetDatePicker datePickerCmd
    )



-- UPDATE


type Msg
    = SetDatePicker DatePicker.Msg
    | ToggleAnimal Animal String
    | FamiliesFetched (Result Http.Error (List Family))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        refreshFamilies newModel =
            case ( newModel.date_debut, newModel.selectedAnimals ) of
                ( _, [] ) ->
                    ( newModel, Cmd.none )

                ( Nothing, _ ) ->
                    ( newModel, Cmd.none )

                ( Just date_debut, selectedAnimals ) ->
                    ( newModel, FamilyCandidates.fetchFamilies model.url date_debut selectedAnimals FamiliesFetched )
    in
    case msg of
        SetDatePicker subMsg ->
            let
                ( newDatePicker, dateEvent ) =
                    DatePicker.update datePickerSettings subMsg model.dateDebutPicker

                date =
                    case dateEvent of
                        Picked newDate ->
                            Just newDate

                        _ ->
                            model.date_debut

                newModel =
                    { model
                        | date_debut = date
                        , dateDebutPicker = newDatePicker
                    }
            in
            refreshFamilies newModel

        ToggleAnimal animal _ ->
            let
                newModel =
                    if List.member animal model.selectedAnimals then
                        { model | selectedAnimals = List.filter (\a -> a /= animal) model.selectedAnimals }

                    else
                        { model | selectedAnimals = animal :: model.selectedAnimals }
            in
            refreshFamilies newModel

        FamiliesFetched (Err err) ->
            ( { model | families = [] }, Cmd.none )

        FamiliesFetched (Ok families) ->
            ( { model | families = families }, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none



-- VIEW


datePickerSettings : DatePicker.Settings
datePickerSettings =
    { defaultSettings
        | inputId = Just "id_date_debut"
        , inputName = Just "date_debut"
        , placeholder = "Choisissez une date début…"
        , dateFormatter = Date.format "dd/MM/yyyy"
    }


view : Model -> Html Msg
view model =
    div [ class "p-2" ]
        [ viewDatePicker model
        , viewAnimals model.animals model.selectedAnimals
        , viewFamilyTable model.families
        ]


viewDatePicker : Model -> Html Msg
viewDatePicker model =
    p []
        [ label [ for "id_date_debut" ] [ text "Date de début :" ]
        , DatePicker.view
            model.date_debut
            datePickerSettings
            model.dateDebutPicker
            |> Html.map SetDatePicker
        ]


viewAnimals : List Animal -> List Animal -> Html Msg
viewAnimals animals selectedAnimals =
    div []
        [ p []
            [ label []
                [ text "Animaux :" ]
            ]
        , List.map (viewAnimal selectedAnimals) animals
            |> ul [ id "id_animaux" ]
        ]


viewAnimal : List Animal -> Animal -> Html Msg
viewAnimal selectedAnimals animal =
    let
        html_id =
            "id_animaux_" ++ String.fromInt animal.id

        is_checked =
            List.member animal selectedAnimals
    in
    li []
        [ label [ for html_id ]
            [ input
                [ id html_id
                , name "animaux"
                , type_ "checkbox"
                , value <| String.fromInt animal.id
                , onInput <| ToggleAnimal animal
                , checked is_checked
                ]
                []
            , text <| " " ++ animal.label
            ]
        ]


viewFamilyTable : List Family -> Html Msg
viewFamilyTable families =
    let
        firstId =
            case families of
                first :: _ ->
                    first.id

                _ ->
                    0
    in
    table [ class "display table table-sm table-bordered", id "famille" ]
        [ thead []
            [ tr []
                [ th [ class "no-sort" ]
                    []
                , th []
                    [ text "Places Disponibles" ]
                , th []
                    [ text "Personne" ]
                , th []
                    [ text "Disponibilité" ]
                , th []
                    [ text "Caractéristiques" ]
                , th []
                    [ text "Commentaire" ]
                ]
            ]
        , if List.length families == 0 then
            tbody [] [ tr [] [ td [ colspan 6, class "text-center" ] [ text "Aucune famille disponible" ] ] ]

          else
            List.map (viewFamily firstId) families |> tbody []
        ]


viewFamily : Int -> Family -> Html Msg
viewFamily firstId family =
    tr []
        [ td []
            [ input
                [ class "tableselectmultiple selectable-checkbox form-check-input"
                , id <| "id_famille_" ++ String.fromInt family.id
                , name "famille"
                , type_ "radio"
                , required True
                , checked <| firstId == family.id
                , value <| String.fromInt family.id
                ]
                []
            ]
        , td [] [ text family.places_disponible ]
        , td [] [ text family.personne ]
        , td [] [ text family.disponibilites ]
        , td [] [ pre [] [ text family.caracteristiques ] ]
        , td [] [ text family.commentaire ]
        ]
